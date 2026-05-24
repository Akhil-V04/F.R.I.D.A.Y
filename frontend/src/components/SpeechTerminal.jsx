import React, { useState, useEffect, useRef, useCallback } from 'react';
import './SpeechTerminal.css';

export default function SpeechTerminal() {
  const [currentUserText, setCurrentUserText] = useState('');
  const [currentFridayText, setCurrentFridayText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const typewriterIntervalRef = useRef(null);
  const finalTranscriptRef = useRef('');
  const silenceTimeoutRef = useRef(null);

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.error('Speech Recognition API not supported');
      alert('Speech Recognition not supported in your browser');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    const startListening = () => {
      try {
        console.log('🎤 Starting to listen...');
        recognition.start();
      } catch (error) {
        console.log('Recognition already running or starting');
      }
    };

    recognition.onstart = () => {
      console.log('✅ Listening active');
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        console.log('Transcript:', transcript);

        if (event.results[i].isFinal) {
          finalTranscriptRef.current += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      const fullText = finalTranscriptRef.current + interimTranscript;
      console.log('📝 Full text:', fullText);
      setCurrentUserText(fullText);

      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }

      silenceTimeoutRef.current = setTimeout(() => {
        if (fullText.trim() && !currentFridayText) {
          console.log('🤖 Generating response');
          generateFridayResponse(fullText.trim());
          finalTranscriptRef.current = '';
        }
      }, 1500);
    };

    recognition.onend = () => {
      console.log('⏹️ Listening stopped, restarting...');
      setIsListening(false);
      setTimeout(() => {
        startListening();
      }, 500);
    };

    recognition.onerror = (event) => {
      console.error('❌ Error:', event.error);
      if (event.error === 'network') {
        console.log('Network error - likely no internet for speech service');
      }
      setTimeout(() => {
        startListening();
      }, 1000);
    };

    recognitionRef.current = recognition;

    // Request microphone permission first
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(() => {
        console.log('✅ Microphone permission granted');
        startListening();
      })
      .catch((error) => {
        console.error('❌ Microphone permission denied:', error);
        alert('Please allow microphone access to use speech recognition');
      });

    return () => {
      if (recognition) {
        recognition.abort();
      }
    };
  }, []);

  // Typewriter effect for F.R.I.D.A.Y responses
  const typewriterEffect = (text) => {
    let index = 0;
    setCurrentFridayText('');

    const interval = setInterval(() => {
      if (index < text.length) {
        setCurrentFridayText((prev) => prev + text[index]);
        index++;
      } else {
        clearInterval(interval);
        // Auto-clear after response finishes
        setTimeout(() => {
          setCurrentFridayText('');
          setCurrentUserText('');
        }, 2000);
      }
    }, 30);

    typewriterIntervalRef.current = interval;
  };

  // Generate F.R.I.D.A.Y response
  const generateFridayResponse = useCallback((userMessage) => {
    // If user interrupted, cancel current F.R.I.D.A.Y response
    if (typewriterIntervalRef.current) {
      clearInterval(typewriterIntervalRef.current);
    }

    const mockResponses = [
      "Processing your request... One moment please.",
      "Understood. Executing task now.",
      "Affirmative. This has been noted.",
      "Very well. I am on it.",
      "Right away. Initializing protocol.",
      "As you wish. Commencing sequence.",
    ];

    const randomResponse =
      mockResponses[Math.floor(Math.random() * mockResponses.length)];

    setTimeout(() => {
      typewriterEffect(randomResponse);
    }, 300);
  }, []);

  const displayText = currentUserText || currentFridayText;
  const speaker = currentFridayText ? 'F.R.I.D.A.Y' : 'USER';

  return (
    <div className="speech-terminal-bar">
      <div className="terminal-speaker">
        <span className="speaker-name">◆ {speaker} ▸</span>
      </div>

      <div className="terminal-text">
        <span className="text-content">{displayText}</span>
        {displayText && <span className="cursor-blink">_</span>}
      </div>

      <div className="terminal-indicator">
        <div className={`status-light ${isListening || displayText ? 'active' : ''}`}></div>
      </div>
    </div>
  );
}
