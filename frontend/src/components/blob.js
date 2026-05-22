import { useEffect, useRef, useState, useCallback } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

// ─── Noise GLSL (shared by plasma & shell shaders) ───────────
const NOISE_GLSL = `
  vec3 mod289v3(vec3 x){return x-floor(x*(1./289.))*289.;}
  vec4 mod289v4(vec4 x){return x-floor(x*(1./289.))*289.;}
  vec4 permute(vec4 x){return mod289v4(((x*34.)+1.)*x);}
  vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
  float snoise(vec3 v){
    const vec2 C=vec2(1./6.,1./3.);const vec4 D=vec4(0.,.5,1.,2.);
    vec3 i=floor(v+dot(v,C.yyy));vec3 x0=v-i+dot(i,C.xxx);
    vec3 g=step(x0.yzx,x0.xyz);vec3 l=1.-g;
    vec3 i1=min(g.xyz,l.zxy);vec3 i2=max(g.xyz,l.zxy);
    vec3 x1=x0-i1+C.xxx;vec3 x2=x0-i2+C.yyy;vec3 x3=x0-D.yyy;
    i=mod289v3(i);
    vec4 p=permute(permute(permute(i.z+vec4(0.,i1.z,i2.z,1.))+i.y+vec4(0.,i1.y,i2.y,1.))+i.x+vec4(0.,i1.x,i2.x,1.));
    float n_=.142857142857;vec3 ns=n_*D.wyz-D.xzx;
    vec4 j=p-49.*floor(p*ns.z*ns.z);vec4 x_=floor(j*ns.z);vec4 y_=floor(j-7.*x_);
    vec4 x=x_*ns.x+ns.yyyy;vec4 y=y_*ns.x+ns.yyyy;vec4 h=1.-abs(x)-abs(y);
    vec4 b0=vec4(x.xy,y.xy);vec4 b1=vec4(x.zw,y.zw);
    vec4 s0=floor(b0)*2.+1.;vec4 s1=floor(b1)*2.+1.;
    vec4 sh=-step(h,vec4(0.));
    vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy;vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
    vec3 p0=vec3(a0.xy,h.x);vec3 p1=vec3(a0.zw,h.y);vec3 p2=vec3(a1.xy,h.z);vec3 p3=vec3(a1.zw,h.w);
    vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
    p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
    vec4 m=max(.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),.0);
    m=m*m;
    return 42.*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
  }
  float fbm(vec3 p){
    float t=0.,a=.5,f=1.;
    for(int i=0;i<3;i++){t+=snoise(p*f)*a;a*=.5;f*=2.;}
    return t;
  }
`;

const SHELL_VERT = `
  varying vec3 vNormal; varying vec3 vViewPosition;
  void main(){
    vNormal=normalize(normalMatrix*normal);
    vec4 mv=modelViewMatrix*vec4(position,1.);
    vViewPosition=-mv.xyz; gl_Position=projectionMatrix*mv;
  }`;

const SHELL_FRAG = `
  varying vec3 vNormal; varying vec3 vViewPosition;
  uniform vec3 uColor; uniform float uOpacity;
  void main(){
    float f=pow(1.-dot(normalize(vNormal),normalize(vViewPosition)),2.5);
    gl_FragColor=vec4(uColor,f*uOpacity);
  }`;

// ─────────────────────────────────────────────────────────────
export default function PlasmaOrb({
  /** Parent container class — override to size the orb differently */
  className = "",
  /** Called with (isListening: boolean) whenever mic state changes */
  onListeningChange,
}) {
  const mountRef = useRef(null);
  const threeRef = useRef({}); // holds all THREE objects
  const audioRef = useRef({ ctx: null, analyser: null, stream: null, data: null });
  const smoothRef = useRef(0);
  const rafRef = useRef(null);

  const [listening, setListening] = useState(false);
  const [status, setStatus] = useState("IDLE");
  const [level, setLevel] = useState(0);

  // ── Build scene once ────────────────────────────────────────
  useEffect(() => {
    const el = mountRef.current;
    if (!el) return;

    const W = el.clientWidth;
    const H = el.clientHeight;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(W, H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.9;
    el.appendChild(renderer.domElement);

    // Scene / Camera
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, W / H, 0.1, 100);
    camera.position.z = 2.4;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.minDistance = 1.5;
    controls.maxDistance = 20;

    const mainGroup = new THREE.Group();
    scene.add(mainGroup);

    // ── Shell ─────────────────────────────────────────────────
    const shellGeo = new THREE.SphereGeometry(1.0, 64, 64);
    const shellBackMat = new THREE.ShaderMaterial({
      vertexShader: SHELL_VERT, fragmentShader: SHELL_FRAG,
      uniforms: { uColor: { value: new THREE.Color(0x003333) }, uOpacity: { value: 0.4 } },
      transparent: true, blending: THREE.AdditiveBlending,
      side: THREE.BackSide, depthWrite: false,
    });
    const shellFrontMat = new THREE.ShaderMaterial({
      vertexShader: SHELL_VERT, fragmentShader: SHELL_FRAG,
      uniforms: { uColor: { value: new THREE.Color(0x00fff0) }, uOpacity: { value: 0.45 } },
      transparent: true, blending: THREE.AdditiveBlending,
      side: THREE.FrontSide, depthWrite: false,
    });
    mainGroup.add(new THREE.Mesh(shellGeo, shellBackMat));
    mainGroup.add(new THREE.Mesh(shellGeo, shellFrontMat));

    // ── Plasma ─────────────────────────────────────────────────
    const plasmaGeo = new THREE.SphereGeometry(0.998, 128, 128);
    const plasmaMat = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uScale: { value: 0.2 },
        uBrightness: { value: 1.4 },
        uThreshold: { value: 0.09 },
        uAudio: { value: 0.0 },
        uColorDeep: { value: new THREE.Color(0x001a1a) },
        uColorMid: { value: new THREE.Color(0x00a099) },
        uColorBright: { value: new THREE.Color(0x00fff0) },
      },
      vertexShader: `
        varying vec3 vPosition; varying vec3 vNormal; varying vec3 vViewPosition;
        void main(){
          vPosition=position; vNormal=normalize(normalMatrix*normal);
          vec4 mv=modelViewMatrix*vec4(position,1.);
          vViewPosition=-mv.xyz; gl_Position=projectionMatrix*mv;
        }`,
      fragmentShader: `
        uniform float uTime,uScale,uBrightness,uThreshold,uAudio;
        uniform vec3 uColorDeep,uColorMid,uColorBright;
        varying vec3 vPosition,vNormal,vViewPosition;
        ${NOISE_GLSL}
        void main(){
          float ab=uAudio*2.;
          vec3 p=vPosition*(uScale+uAudio*.15);
          float sp=.05+uAudio*.12;
          vec3 q=vec3(fbm(p+vec3(0.,uTime*sp,0.)),fbm(p+vec3(5.2,1.3,2.8)+uTime*sp),fbm(p+vec3(2.2,8.4,.5)-uTime*sp*.4));
          float density=fbm(p+(2.+ab)*q);
          float t=(density+.4)*.8;
          float thr=uThreshold-uAudio*.06;
          float alpha=smoothstep(thr,.7,t);
          vec3 cW=vec3(1.);
          vec3 color=mix(uColorDeep,uColorMid,smoothstep(thr,.5,t));
          color=mix(color,uColorBright,smoothstep(.5,.8,t));
          color=mix(color,cW,smoothstep(.8,1.,t));
          color=mix(color,vec3(.6,1.,.97)*uBrightness,smoothstep(.8,1.,t)*uAudio*.5);
          float facing=dot(normalize(vNormal),normalize(vViewPosition));
          float depth=(facing+1.)*.5;
          float finalAlpha=alpha*(.02+.98*depth);
          gl_FragColor=vec4(color*(uBrightness+uAudio*.8),finalAlpha);
        }`,
      transparent: true, blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide, depthWrite: false,
    });
    const plasmaMesh = new THREE.Mesh(plasmaGeo, plasmaMat);
    mainGroup.add(plasmaMesh);

    // ── Outer glow ────────────────────────────────────────────
    const glowGeo = new THREE.SphereGeometry(1.05, 64, 64);
    const glowMat = new THREE.ShaderMaterial({
      uniforms: { uColor: { value: new THREE.Color(0x00fff0) }, uAudio: { value: 0 }, uTime: { value: 0 } },
      vertexShader: SHELL_VERT,
      fragmentShader: `
        uniform vec3 uColor; uniform float uAudio,uTime;
        varying vec3 vNormal,vViewPosition;
        void main(){
          float f=pow(1.-dot(normalize(vNormal),normalize(vViewPosition)),3.);
          float pulse=1.+uAudio*1.5;
          float flicker=1.+uAudio*.3*sin(uTime*20.);
          gl_FragColor=vec4(uColor,f*.5*pulse*flicker);
        }`,
      transparent: true, blending: THREE.AdditiveBlending,
      side: THREE.FrontSide, depthWrite: false,
    });
    mainGroup.add(new THREE.Mesh(glowGeo, glowMat));

    // ── Particles ─────────────────────────────────────────────
    const pCount = 600;
    const pPos = new Float32Array(pCount * 3);
    const pSizes = new Float32Array(pCount);
    for (let i = 0; i < pCount; i++) {
      const r = 0.95 * Math.cbrt(Math.random());
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      pPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pPos[i * 3 + 2] = r * Math.cos(phi);
      pSizes[i] = Math.random();
    }
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
    pGeo.setAttribute("aSize", new THREE.BufferAttribute(pSizes, 1));
    const pMat = new THREE.ShaderMaterial({
      uniforms: { uTime: { value: 0 }, uColor: { value: new THREE.Color(0x00fff0) }, uAudio: { value: 0 } },
      vertexShader: `
        uniform float uTime,uAudio; attribute float aSize; varying float vAlpha;
        void main(){
          vec3 pos=position;
          float d=.02+uAudio*.04;
          pos.y+=sin(uTime*.2+pos.x*3.)*d; pos.x+=cos(uTime*.15+pos.z*3.)*d;
          vec4 mv=modelViewMatrix*vec4(pos,1.);gl_Position=projectionMatrix*mv;
          float bs=(8.*aSize+4.)*(1.+uAudio*1.5)*(1./-mv.z);
          gl_PointSize=bs;
          vAlpha=(0.8+0.2*sin(uTime+aSize*10.))*(.5+uAudio*.5);
        }`,
      fragmentShader: `
        uniform vec3 uColor; varying float vAlpha;
        void main(){
          vec2 uv=gl_PointCoord-vec2(.5);float d=length(uv);if(d>.5)discard;
          float glow=pow(1.-d*2.,1.8);gl_FragColor=vec4(uColor,glow*vAlpha);
        }`,
      transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
    });
    mainGroup.add(new THREE.Points(pGeo, pMat));

    // ── Store refs ────────────────────────────────────────────
    threeRef.current = { renderer, scene, camera, controls, mainGroup, plasmaMesh, plasmaMat, shellFrontMat, glowMat, pMat };

    // ── Animation loop ────────────────────────────────────────
    const clock = new THREE.Clock();

    function animate() {
      rafRef.current = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();
      const a = audioRef.current;

      // Compute audio level
      let raw = 0;
      if (a.analyser && a.data) {
        a.analyser.getByteFrequencyData(a.data);
        const start = Math.floor(a.data.length * 0.02);
        const end = Math.floor(a.data.length * 0.4);
        let sum = 0;
        for (let i = start; i < end; i++) sum += a.data[i];
        raw = Math.min(sum / (end - start) / 128, 1);
      }

      // Fast attack / slow decay
      const prev = smoothRef.current;
      smoothRef.current = raw > prev
        ? prev + (raw - prev) * 0.35
        : prev + (raw - prev) * 0.06;

      const al = smoothRef.current;

      // Update uniforms
      plasmaMat.uniforms.uTime.value = t * (1.2 + al * 1.8);
      plasmaMat.uniforms.uAudio.value = al;
      glowMat.uniforms.uAudio.value = al;
      glowMat.uniforms.uTime.value = t;
      pMat.uniforms.uTime.value = t;
      pMat.uniforms.uAudio.value = al;
      shellFrontMat.uniforms.uOpacity.value = 0.45 + al * 0.55;

      // Scale
      const idlePulse = 1.0 + Math.sin(t * 1.2) * 0.005;
      mainGroup.scale.setScalar(idlePulse * (1 + al * 0.15));

      // Rotation
      plasmaMesh.rotation.y = t * 0.08;
      mainGroup.rotation.x += 0.002 + al * 0.008;
      mainGroup.rotation.y += 0.005 + al * 0.015;

      controls.update();
      renderer.render(scene, camera);

      // Throttled React state update (every ~6 frames)
      if (Math.round(t * 60) % 6 === 0) {
        setLevel(Math.round(al * 100));
      }
    }
    animate();

    // ── Resize ────────────────────────────────────────────────
    const ro = new ResizeObserver(() => {
      const w = el.clientWidth;
      const h = el.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
    ro.observe(el);

    return () => {
      cancelAnimationFrame(rafRef.current);
      ro.disconnect();
      renderer.dispose();
      el.removeChild(renderer.domElement);
    };
  }, []);

  // ── Mic controls ────────────────────────────────────────────
  const startMic = useCallback(async () => {
    try {
      setStatus("REQUESTING...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;
      const data = new Uint8Array(analyser.frequencyBinCount);
      ctx.createMediaStreamSource(stream).connect(analyser);
      audioRef.current = { ctx, analyser, stream, data };
      setListening(true);
      setStatus("LISTENING");
      onListeningChange?.(true);
    } catch {
      setStatus("MIC DENIED");
    }
  }, [onListeningChange]);

  const stopMic = useCallback(() => {
    const a = audioRef.current;
    a.stream?.getTracks().forEach((t) => t.stop());
    a.ctx?.close();
    audioRef.current = { ctx: null, analyser: null, stream: null, data: null };
    smoothRef.current = 0;
    setListening(false);
    setStatus("IDLE");
    setLevel(0);
    onListeningChange?.(false);
  }, [onListeningChange]);

  const toggleMic = () => (listening ? stopMic() : startMic());

  // ── Render ───────────────────────────────────────────────────
  return (
    <div
      className={className}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        background: "#000",
        overflow: "hidden",
      }}
    >
      {/* Three.js canvas mount */}
      <div ref={mountRef} style={{ width: "100%", height: "100%" }} />

      {/* HUD */}
      <div
        style={{
          position: "absolute",
          bottom: 24,
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 12,
          pointerEvents: "none",
          fontFamily: "'Courier New', monospace",
        }}
      >
        {/* Level bar */}
        <div style={{ width: 160, height: 2, background: "rgba(0,255,240,0.15)", borderRadius: 1, overflow: "hidden" }}>
          <div
            style={{
              height: "100%",
              width: `${level}%`,
              background: "linear-gradient(90deg,#00b8b0,#00fff0,#fff)",
              boxShadow: "0 0 8px #00fff0",
              transition: "width 0.05s",
            }}
          />
        </div>

        {/* Status */}
        <div
          style={{
            color: "#00fff0",
            fontSize: 10,
            letterSpacing: "0.25em",
            textTransform: "uppercase",
            opacity: 0.7,
            textShadow: "0 0 10px #00fff0",
          }}
        >
          {status}
        </div>

        {/* Button */}
        <button
          onClick={toggleMic}
          style={{
            pointerEvents: "all",
            background: listening ? "rgba(0,255,240,0.12)" : "transparent",
            border: "1px solid #00fff0",
            color: "#00fff0",
            padding: "10px 28px",
            fontFamily: "'Courier New', monospace",
            fontSize: 11,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            cursor: "pointer",
            boxShadow: listening
              ? "0 0 32px rgba(0,255,240,0.6), inset 0 0 20px rgba(0,255,240,0.15)"
              : "0 0 12px rgba(0,255,240,0.2), inset 0 0 12px rgba(0,255,240,0.05)",
            transition: "all 0.3s",
          }}
        >
          {listening ? "Deactivate Mic" : "Activate Mic"}
        </button>
      </div>
    </div>
  );
}