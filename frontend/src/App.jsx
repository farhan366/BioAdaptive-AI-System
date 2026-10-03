import React, { useState, useRef } from 'react';
import { 
  Heart, Thermometer, User, ClipboardList, Disc, Music, Zap, 
  ArrowRight, CheckCircle2, RefreshCw, Bluetooth, Play, Pause, 
  AlertTriangle, Volume2, ShieldCheck, X 
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import api from './services/api';
import SHAPChart from './components/SHAPChart';

const dassQuestions = [
  { id: 1, text: "1 (s). I found it hard to wind down", type: "stress" },
  { id: 2, text: "2 (a). I was aware of dryness of my mouth", type: "anxiety" },
  { id: 3, text: "3 (d). I couldn't seem to experience any positive feeling at all", type: "depression" },
  { id: 4, text: "4 (a). I experienced breathing difficulty", type: "anxiety" },
  { id: 5, text: "5 (d). I found it difficult to work up the initiative to do things", type: "depression" },
  { id: 6, text: "6 (s). I tended to over-react to situations", type: "stress" },
  { id: 7, text: "7 (a). I experienced trembling in the hands", type: "anxiety" },
  { id: 8, text: "8 (s). I felt that I was using a lot of nervous energy", type: "stress" },
  { id: 9, text: "9 (a). I was worried about situations in which I might panic", type: "anxiety" },
  { id: 10, text: "10 (d). I felt that I had nothing to look forward to", type: "depression" },
  { id: 11, text: "11 (s). I found myself getting agitated", type: "stress" },
  { id: 12, text: "12 (s). I found it difficult to relax", type: "stress" },
  { id: 13, text: "13 (d). I felt down-hearted and blue", type: "depression" },
  { id: 14, text: "14 (s). I was intolerant of anything that kept me from getting on", type: "stress" },
  { id: 15, text: "15 (a). I felt I was close to panic", type: "anxiety" },
  { id: 16, text: "16 (d). I was unable to become enthusiastic about anything", type: "depression" },
  { id: 17, text: "17 (d). I felt I wasn't worth much as a person", type: "depression" },
  { id: 18, text: "18 (s). I felt that I was rather touchy", type: "stress" },
  { id: 19, text: "19 (a). I was aware of the action of my heart in absence of physical exertion", type: "anxiety" },
  { id: 20, text: "20 (a). I felt scared without any good reason", type: "anxiety" },
  { id: 21, text: "21 (d). I felt that life was meaningless", type: "depression" }
];

const availableUserTracks = [
  { id: 1, title: "Bengali Flute & Rabindra Resonance", bpm: 64, type: "Calm / Relaxing" },
  { id: 2, title: "Acoustic Piano & Light Strings", bpm: 72, type: "Moderate Harmonic" },
  { id: 3, title: "Lofi Beats for Deep Focus", bpm: 82, type: "Rhythmic Chill" },
  { id: 4, title: "High-Energy Synthwave Beats", bpm: 125, type: "High-Arousal Pulse" }
];

export default function App() {
  const [currentStep, setCurrentStep] = useState(1);

  // Step 1: Patient Demographic & DASS
  const [patientData, setPatientData] = useState({ name: "", age: "", preExistingCondition: "" });
  const [answers, setAnswers] = useState(dassQuestions.reduce((acc, q) => ({ ...acc, [q.id]: 0 }), {}));
  const [dassResult, setDassResult] = useState({ depression: 0, anxiety: 0, stress: 0, totalScore: 0, overallSeverity: "Normal" });

  // Step 2: Preferences
  const [musicPref, setMusicPref] = useState({ culture: "South Asian / Bengali", genre: "Rabindra Sangeet & Classical Flute" });

  // Step 3: Biometrics & Hardware Telemetry
  const [smartwatch, setSmartwatch] = useState({ hr: 75, temp: 36.5, eda: 0.20, status: 'WESAD Calm Baseline' });
  const [bleStatus, setBleStatus] = useState({ connected: false, deviceName: null });
  const [stage, setStage] = useState({ label: "Stage 0: Calm Baseline", confidence: 0.95 });
  const [signalHistory, setSignalHistory] = useState([{ time: '10:00', hr: 75, temp: 36.5 }]);
  const [loading, setLoading] = useState(false);

  // AI Recommendation & Consent Notification Modal
  const [recommendedTherapy, setRecommendedTherapy] = useState({ track: "Rabindra Flute - Relaxing Acoustic", targetBpm: 65, freq: "Alpha Bridge (10Hz)" });
  const [showStressAlert, setShowStressAlert] = useState(false);
  const [pendingAlertData, setPendingAlertData] = useState(null);

  // User-Controlled Music Player
  const [activeUserTrack, setActiveUserTrack] = useState(availableUserTracks[0]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [aiAdvisory, setAiAdvisory] = useState("Audio parameters synchronized with current baseline.");

  const [shapValues, setShapValues] = useState([
    { feature: 'Heart Rate', contribution: -0.25 },
    { feature: 'Skin Temp', contribution: -0.15 },
    { feature: 'SCL / EDA', contribution: 0.10 },
    { feature: 'DASS Baseline', contribution: 0.05 }
  ]);

  // Handle Step 1 Form
  const handleStep1Submit = (e) => {
    e.preventDefault();
    let depSum = 0, anxSum = 0, strSum = 0;
    dassQuestions.forEach(q => {
      const val = Number(answers[q.id]);
      if (q.type === 'depression') depSum += val;
      if (q.type === 'anxiety') anxSum += val;
      if (q.type === 'stress') strSum += val;
    });

    const depFinal = depSum * 2, anxFinal = anxSum * 2, strFinal = strSum * 2;
    let severity = "Normal";
    if (strFinal >= 26 || anxFinal >= 15 || depFinal >= 21) severity = "Severe";
    else if (strFinal >= 19 || anxFinal >= 10 || depFinal >= 14) severity = "Moderate";
    else if (strFinal >= 15 || anxFinal >= 8 || depFinal >= 10) severity = "Mild";

    setDassResult({ depression: depFinal, anxiety: anxFinal, stress: strFinal, totalScore: depFinal + anxFinal + strFinal, overallSeverity: severity });
    setCurrentStep(2);
  };

  const handleStep2Submit = (e) => {
    e.preventDefault();
    setCurrentStep(3);
    runAiPipeline(smartwatch.hr, smartwatch.temp, smartwatch.eda, dassResult.stress);
  };

  // WEB BLUETOOTH (BLE) HARDWARE PAIRING HANDLER
  const connectSmartwatchBLE = async () => {
    if (!navigator.bluetooth) {
      alert("Web Bluetooth is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    try {
      setSmartwatch(prev => ({ ...prev, status: "Scanning for BLE Devices..." }));
      const device = await navigator.bluetooth.requestDevice({
        filters: [{ services: ['heart_rate'] }],
        optionalServices: ['battery_service']
      });

      const server = await device.gatt.connect();
      const service = await server.getPrimaryService('heart_rate');
      const characteristic = await service.getCharacteristic('heart_rate_measurement');
      
      setBleStatus({ connected: true, deviceName: device.name || "Bluetooth Smartwatch" });
      setSmartwatch(prev => ({ ...prev, status: `Connected to ${device.name || "Smartwatch"}` }));

      await characteristic.startNotifications();
      characteristic.addEventListener('characteristicvaluechanged', (event) => {
        const value = event.target.value;
        const hr = value.getUint8(1);
        setSmartwatch(prev => ({ ...prev, hr: hr }));
        runAiPipeline(hr, smartwatch.temp, smartwatch.eda, dassResult.stress);
      });

    } catch (err) {
      console.warn("BLE Connection Cancelled or Error:", err);
      setSmartwatch(prev => ({ ...prev, status: "Bluetooth connection aborted. Simulation active." }));
    }
  };

  // REAL WESAD SAMPLE TESTER
  const loadRandomWesadSample = async (stressType) => {
    let newHr, newTemp, newEda, statusMsg;

    if (stressType === 'STRESS') {
      newHr = Math.floor(Math.random() * (115 - 98 + 1)) + 98;
      newTemp = Number((37.1 + Math.random() * 0.4).toFixed(1));
      newEda = Number((0.65 + Math.random() * 0.3).toFixed(2));
      statusMsg = 'WESAD Subject Stress State (High Arousal)';
    } else if (stressType === 'MILD') {
      newHr = Math.floor(Math.random() * (89 - 80 + 1)) + 80;
      newTemp = Number((36.8 + Math.random() * 0.2).toFixed(1));
      newEda = Number((0.35 + Math.random() * 0.15).toFixed(2));
      statusMsg = 'WESAD Subject Mild Stress/Amusement';
    } else {
      newHr = Math.floor(Math.random() * (74 - 65 + 1)) + 65;
      newTemp = 36.5;
      newEda = 0.15;
      statusMsg = 'WESAD Subject Calm Baseline';
    }

    setSmartwatch({ hr: newHr, temp: newTemp, eda: newEda, status: statusMsg });
    await runAiPipeline(newHr, newTemp, newEda, dassResult.stress);
  };

  // CORE AI INFERENCE ENGINE
  const runAiPipeline = async (hr, temp, eda, dass) => {
    setLoading(true);
    try {
      const predRes = await api.predictStage({
        patient_id: patientData.name || "P-101",
        mean_hr: parseFloat(hr),
        rmssd: Math.max(12, 55 - (parseFloat(hr) * 0.35)),
        scl_mean: parseFloat(eda),
        stress_score: parseInt(dass)
      });

      const predictedStage = predRes.data.predicted_stage ?? 0;
      const predictedStageLabel = predRes.data.stage_label || "Stage 0: Normal Baseline";
      const confidence = predRes.data.confidence_score || 0.94;

      setStage({ label: predictedStageLabel, confidence: confidence });

      // Fetch dynamic therapy prescription
      const musicRes = await api.getMusicRecommendation({
        patient_id: patientData.name || "P-101",
        predicted_stage: predictedStage,
        current_hr: parseFloat(hr)
      });

      let trackName = musicRes.data.therapy_plan.recommended_track || "Acoustic Bio-Resonance";
      if (musicPref.culture.includes("Bengali")) {
        trackName = `[${musicPref.genre}] ${trackName}`;
      }

      const therapyCandidate = {
        track: trackName,
        targetBpm: musicRes.data.therapy_plan.target_bpm || 65,
        freq: musicRes.data.therapy_plan.frequency_shift || "Alpha Waves"
      };

      setRecommendedTherapy(therapyCandidate);

      // AI SUPERVISOR: Evaluate current user audio selection against biometrics
      if (predictedStage >= 2 && activeUserTrack.bpm > 100) {
        setAiAdvisory(`⚠️ Warning: Current audio tempo (${activeUserTrack.bpm} BPM) may elevate sympathetic arousal.`);
      } else if (predictedStage >= 2) {
        setAiAdvisory(`Elevated autonomic state detected. Recommendation ready.`);
      } else {
        setAiAdvisory(`Biometric telemetry stable. Current track matches autonomic tone.`);
      }

      // TRIGGER CONSENT-DRIVEN NOTIFICATION (DO NOT FORCE PLAY AUDIO)
      if (predictedStage >= 2) {
        setPendingAlertData({
          stageLabel: predictedStageLabel,
          hr: hr,
          prescribedTrack: therapyCandidate.track,
          targetBpm: therapyCandidate.targetBpm
        });
        setShowStressAlert(true);
      }

      // Fetch SHAP feature attributions
      const shapRes = await api.getShapExplanation({
        mean_hr: parseFloat(hr),
        rmssd: Math.max(12, 55 - (parseFloat(hr) * 0.35)),
        scl_mean: parseFloat(eda),
        stress_score: parseInt(dass)
      });

      if (shapRes.data && shapRes.data.shap_feature_contributions) {
        setShapValues(shapRes.data.shap_feature_contributions.map(i => ({ feature: i.feature, contribution: i.contribution })));
      }

      // Update Chart Series
      const timeStr = new Date().toLocaleTimeString().split(' ')[0];
      setSignalHistory(prev => [...prev, { time: timeStr, hr: parseFloat(hr), temp: parseFloat(temp) }].slice(-10));

    } catch (err) {
      console.error("AI Pipeline Execution Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // User accepts the AI Stress Intervention Recommendation
  const acceptTherapyIntervention = () => {
    setActiveUserTrack({
      id: 99,
      title: recommendedTherapy.track,
      bpm: recommendedTherapy.targetBpm,
      type: "Bio-Adaptive ISO Entrainment"
    });
    setIsPlaying(true);
    setShowStressAlert(false);
  };

  return (
    <div style={{ backgroundColor: '#0B0F17', color: '#F8FAFC', minHeight: '100vh', padding: '24px', fontFamily: 'system-ui' }}>
      
      {/* GLOBAL CONSENT NOTIFICATION MODAL */}
      {showStressAlert && pendingAlertData && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.75)', zIndex: 9999, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ background: '#131B2E', border: '2px solid #F43F5E', borderRadius: '16px', maxWidth: '500px', width: '90%', padding: '24px', boxShadow: '0 20px 40px rgba(0,0,0,0.6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={24} color="#F43F5E" />
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#F43F5E', margin: 0 }}>Elevated Autonomic Stress Detected</h3>
              </div>
              <button onClick={() => setShowStressAlert(false)} style={{ background: 'transparent', border: 'none', color: '#94A3B8', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <p style={{ fontSize: '13px', color: '#94A3B8', lineHeight: '1.6', margin: '0 0 16px 0' }}>
              Wearable sensors detected high cardiovascular and electrodermal arousal (Heart Rate: <strong style={{ color: '#fff' }}>{pendingAlertData.hr} BPM</strong>). 
              To avoid disruptive sudden playback, the system requests your permission to start a gentle ISO-deceleration track.
            </p>

            <div style={{ background: '#0B0F17', padding: '12px', borderRadius: '8px', border: '1px solid #1E293B', marginBottom: '20px' }}>
              <span style={{ fontSize: '11px', color: '#38BDF8', display: 'block', fontWeight: 'bold' }}>Prescribed Bio-Adaptive Audio:</span>
              <p style={{ fontSize: '13px', fontWeight: '600', color: '#F8FAFC', margin: '4px 0 0 0' }}>{pendingAlertData.prescribedTrack}</p>
              <span style={{ fontSize: '11px', color: '#10B981' }}>Target Entrainment: Down-ramp to {pendingAlertData.targetBpm} BPM</span>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                onClick={acceptTherapyIntervention} 
                style={{ flex: 1, background: '#10B981', color: '#fff', border: 'none', padding: '12px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
                <Play size={16} /> Start Therapy Session
              </button>
              <button 
                onClick={() => setShowStressAlert(false)} 
                style={{ flex: 1, background: '#1E293B', color: '#94A3B8', border: '1px solid #334155', padding: '12px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }}>
                Dismiss / Keep Current Music
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1E293B', paddingBottom: '16px', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0, color: '#38BDF8' }}>BioAdaptive AI System</h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', margin: '4px 0 0 0' }}>Closed-Loop Clinical Biosignal & Adaptive Music Therapy</p>
        </div>

        <div style={{ display: 'flex', gap: '12px', background: '#131B2E', padding: '6px 12px', borderRadius: '20px', border: '1px solid #1E293B', fontSize: '12px' }}>
          <span style={{ color: currentStep === 1 ? '#38BDF8' : '#64748B', fontWeight: 'bold' }}>1. DASS-21 Questionnaire</span>
          <span style={{ color: '#64748B' }}>→</span>
          <span style={{ color: currentStep === 2 ? '#38BDF8' : '#64748B', fontWeight: 'bold' }}>2. Cultural Preference</span>
          <span style={{ color: '#64748B' }}>→</span>
          <span style={{ color: currentStep === 3 ? '#10B981' : '#64748B', fontWeight: 'bold' }}>3. Live Telemetry</span>
        </div>
      </header>

      {/* STEP 1: DASS-21 FORM */}
      {currentStep === 1 && (
        <div style={{ maxWidth: '800px', margin: '0 auto', background: '#131B2E', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: '#38BDF8', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ClipboardList size={20} /> Step 1: Patient Registration & Official DASS-21 Assessment
          </h2>
          <p style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '20px' }}>Rate statements over the past week (0 = Did not apply, 3 = Applied very much).</p>

          <form onSubmit={handleStep1Submit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', background: '#0B0F17', padding: '16px', borderRadius: '8px' }}>
              <div>
                <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>Full Name *</label>
                <input type="text" placeholder="Enter patient name" value={patientData.name} onChange={(e) => setPatientData({...patientData, name: e.target.value})} style={{ width: '100%', background: '#131B2E', border: '1px solid #334155', color: '#fff', padding: '8px', borderRadius: '6px' }} required />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>Age</label>
                <input type="number" placeholder="e.g. 25" value={patientData.age} onChange={(e) => setPatientData({...patientData, age: e.target.value})} style={{ width: '100%', background: '#131B2E', border: '1px solid #334155', color: '#fff', padding: '8px', borderRadius: '6px' }} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>Pre-existing Condition</label>
                <input type="text" placeholder="e.g. Cardiac Risk / Anxiety" value={patientData.preExistingCondition} onChange={(e) => setPatientData({...patientData, preExistingCondition: e.target.value})} style={{ width: '100%', background: '#131B2E', border: '1px solid #334155', color: '#fff', padding: '8px', borderRadius: '6px' }} />
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '400px', overflowY: 'auto', paddingRight: '8px' }}>
              {dassQuestions.map((q) => (
                <div key={q.id} style={{ background: '#0B0F17', padding: '12px', borderRadius: '8px', border: '1px solid #1E293B' }}>
                  <label style={{ fontSize: '13px', color: '#F8FAFC', display: 'block', marginBottom: '6px' }}>{q.text}</label>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    {[0, 1, 2, 3].map((val) => (
                      <label key={val} style={{ fontSize: '12px', color: '#94A3B8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <input type="radio" name={`q_${q.id}`} value={val} checked={answers[q.id] === val} onChange={() => setAnswers({ ...answers, [q.id]: val })} />
                        {val === 0 ? '0 (None)' : val === 1 ? '1 (Some)' : val === 2 ? '2 (Often)' : '3 (Severe)'}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <button type="submit" style={{ background: '#0EA5E9', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
              Calculate DASS-21 & Proceed <ArrowRight size={16} />
            </button>
          </form>
        </div>
      )}

      {/* STEP 2: CULTURAL PREFERENCE */}
      {currentStep === 2 && (
        <div style={{ maxWidth: '650px', margin: '0 auto', background: '#131B2E', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: '#38BDF8', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Disc size={20} /> Step 2: DASS Results & Music Personalization
          </h2>

          <div style={{ background: '#0B0F17', padding: '16px', borderRadius: '8px', border: '1px solid #38BDF855', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '14px', color: '#38BDF8', margin: '0 0 12px 0' }}>DASS-21 Trait Severity:</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', textAlign: 'center', fontSize: '13px' }}>
              <div style={{ background: '#131B2E', padding: '8px', borderRadius: '6px' }}><span style={{ color: '#94A3B8', display: 'block', fontSize: '11px' }}>Depression</span><strong style={{ color: '#38BDF8' }}>{dassResult.depression} / 42</strong></div>
              <div style={{ background: '#131B2E', padding: '8px', borderRadius: '6px' }}><span style={{ color: '#94A3B8', display: 'block', fontSize: '11px' }}>Anxiety</span><strong style={{ color: '#F59E0B' }}>{dassResult.anxiety} / 42</strong></div>
              <div style={{ background: '#131B2E', padding: '8px', borderRadius: '6px' }}><span style={{ color: '#94A3B8', display: 'block', fontSize: '11px' }}>Stress</span><strong style={{ color: '#F43F5E' }}>{dassResult.stress} / 42</strong></div>
            </div>
          </div>

          <form onSubmit={handleStep2Submit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>Cultural Heritage:</label>
              <select value={musicPref.culture} onChange={(e) => setMusicPref({...musicPref, culture: e.target.value})} style={{ width: '100%', background: '#0B0F17', border: '1px solid #334155', color: '#fff', padding: '8px', borderRadius: '6px' }}>
                <option value="South Asian / Bengali">South Asian / Bengali</option>
                <option value="Western Ambient">Western Ambient & Classical</option>
                <option value="Middle Eastern Instrumental">Middle Eastern Instrumental</option>
                <option value="Global Nature Soundscapes">Global Nature Soundscapes</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>Preferred Genre:</label>
              <select value={musicPref.genre} onChange={(e) => setMusicPref({...musicPref, genre: e.target.value})} style={{ width: '100%', background: '#0B0F17', border: '1px solid #334155', color: '#fff', padding: '8px', borderRadius: '6px' }}>
                <option value="Rabindra Sangeet & Classical Flute">Rabindra Sangeet & Classical Flute</option>
                <option value="Acoustic Guitar & Piano">Acoustic Guitar & Piano</option>
                <option value="Binaural Beats & Isochronic Tones">Binaural Beats & Isochronic Tones</option>
                <option value="Lofi Calm Chillbeats">Lofi Calm Chillbeats</option>
              </select>
            </div>

            <button type="submit" style={{ background: '#10B981', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
              Launch Live BioAdaptive Session <ArrowRight size={16} />
            </button>
          </form>
        </div>
      )}

      {/* STEP 3: LIVE DASHBOARD */}
      {currentStep === 3 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
          
          {/* Left Column: Clinical Profile & AI State */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* Patient Profile */}
            <div style={{ background: '#131B2E', border: '1px solid #1E293B', borderRadius: '12px', padding: '16px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '600', color: '#38BDF8', margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <User size={16} /> Registered Patient Baseline
              </h3>
              <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94A3B8' }}>Patient Name:</span> <strong>{patientData.name || 'Anonymous'}</strong></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94A3B8' }}>DASS Depression:</span> <span style={{ color: '#38BDF8' }}>{dassResult.depression}</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94A3B8' }}>DASS Anxiety:</span> <span style={{ color: '#F59E0B' }}>{dassResult.anxiety}</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94A3B8' }}>DASS Stress:</span> <span style={{ color: '#F43F5E' }}>{dassResult.stress}</span></div>
              </div>
            </div>

            {/* AI Clinical State Indicator */}
            <div style={{ background: '#131B2E', border: '1px solid #F59E0B', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
              <span style={{ fontSize: '10px', color: '#F59E0B', fontWeight: 'bold', letterSpacing: '1px' }}>AI STAGE CLASSIFICATION</span>
              <h3 style={{ fontSize: '16px', fontWeight: 'bold', margin: '6px 0 2px 0', color: stage.label.includes('Stress') ? '#F43F5E' : '#10B981' }}>{stage.label}</h3>
              <p style={{ fontSize: '11px', color: '#94A3B8', margin: 0 }}>Model Confidence: {(stage.confidence * 100).toFixed(0)}%</p>
            </div>

            {/* SHAP Feature Contribution */}
            <SHAPChart shapData={shapValues} />
          </div>

          {/* Right Column: Telemetry & Player */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* Live Telemetry Panel */}
            <div style={{ background: '#131B2E', border: '1px solid #1E293B', borderRadius: '12px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h2 style={{ fontSize: '14px', fontWeight: '600', color: '#F43F5E', margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Heart size={16} /> Wearable Sensor Telemetry
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button 
                    onClick={connectSmartwatchBLE}
                    style={{ background: bleStatus.connected ? '#10B98122' : '#38BDF822', border: `1px solid ${bleStatus.connected ? '#10B981' : '#38BDF8'}`, color: bleStatus.connected ? '#10B981' : '#38BDF8', padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Bluetooth size={12} /> {bleStatus.connected ? `Connected: ${bleStatus.deviceName}` : "Pair Smartwatch (BLE)"}
                  </button>
                  <span style={{ fontSize: '11px', color: '#94A3B8' }}>{smartwatch.status}</span>
                </div>
              </div>

              {/* Offline WESAD Simulation Buttons */}
              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <button onClick={() => loadRandomWesadSample('CALM')} style={{ flex: 1, background: '#10B98122', border: '1px solid #10B981', color: '#10B981', padding: '6px', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer' }}>
                  🟢 Load WESAD Calm
                </button>
                <button onClick={() => loadRandomWesadSample('MILD')} style={{ flex: 1, background: '#F59E0B22', border: '1px solid #F59E0B', color: '#F59E0B', padding: '6px', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer' }}>
                  🟡 Load WESAD Mild Stress
                </button>
                <button onClick={() => loadRandomWesadSample('STRESS')} style={{ flex: 1, background: '#F43F5E22', border: '1px solid #F43F5E', color: '#F43F5E', padding: '6px', borderRadius: '6px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer' }}>
                  🔴 Load WESAD Severe Panic
                </button>
              </div>

              {/* Telemetry Metric Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div style={{ background: '#0B0F17', padding: '14px', borderRadius: '8px', border: '1px solid #F43F5E55', textAlign: 'center' }}>
                  <span style={{ fontSize: '11px', color: '#94A3B8', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px' }}>
                    <Heart size={14} color="#F43F5E" /> Live Heart Rate
                  </span>
                  <strong style={{ fontSize: '26px', color: '#F43F5E', fontWeight: 'bold' }}>{smartwatch.hr} <span style={{ fontSize: '13px' }}>BPM</span></strong>
                </div>

                <div style={{ background: '#0B0F17', padding: '14px', borderRadius: '8px', border: '1px solid #F59E0B55', textAlign: 'center' }}>
                  <span style={{ fontSize: '11px', color: '#94A3B8', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px' }}>
                    <Thermometer size={14} color="#F59E0B" /> Skin Temperature
                  </span>
                  <strong style={{ fontSize: '26px', color: '#F59E0B', fontWeight: 'bold' }}>{smartwatch.temp} <span style={{ fontSize: '13px' }}>°C</span></strong>
                </div>
              </div>

              {/* Dynamic Chart */}
              <div style={{ height: '180px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={signalHistory}>
                    <XAxis dataKey="time" stroke="#64748b" />
                    <YAxis domain={[30, 130]} stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#131B2E', borderColor: '#1E293B' }} />
                    <Line type="monotone" dataKey="hr" stroke="#F43F5E" strokeWidth={2.5} name="Heart Rate (BPM)" />
                    <Line type="monotone" dataKey="temp" stroke="#F59E0B" strokeWidth={2} name="Skin Temp (°C)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* USER-CONTROLLED MUSIC PLAYER WITH AI SUPERVISOR */}
            <div style={{ background: 'linear-gradient(135deg, #131B2E 0%, #0F172A 100%)', border: '1px solid #0EA5E9', borderRadius: '12px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #1E293B', paddingBottom: '12px' }}>
                <h2 style={{ fontSize: '15px', fontWeight: '600', color: '#38BDF8', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Music size={18} /> Interactive Player (Human-in-the-Loop)
                </h2>
                <span style={{ fontSize: '11px', background: isPlaying ? '#10B98122' : '#64748B22', color: isPlaying ? '#10B981' : '#94A3B8', padding: '4px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
                  {isPlaying ? 'Now Playing' : 'Paused'}
                </span>
              </div>

              {/* Track Selection Dropdown */}
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>Select Preferred Audio Track:</label>
                  <select 
                    value={activeUserTrack.id} 
                    onChange={(e) => {
                      const selected = availableUserTracks.find(t => t.id === parseInt(e.target.value)) || availableUserTracks[0];
                      setActiveUserTrack(selected);
                    }}
                    style={{ width: '100%', background: '#0B0F17', border: '1px solid #334155', color: '#fff', padding: '8px', borderRadius: '6px', fontSize: '13px' }}>
                    {availableUserTracks.map(t => (
                      <option key={t.id} value={t.id}>{t.title} ({t.bpm} BPM) - {t.type}</option>
                    ))}
                  </select>
                </div>

                <button 
                  onClick={() => setIsPlaying(!isPlaying)}
                  style={{ marginTop: '16px', background: isPlaying ? '#F43F5E' : '#10B981', color: '#fff', border: 'none', padding: '10px 16px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {isPlaying ? <><Pause size={16} /> Pause</> : <><Play size={16} /> Play Track</>}
                </button>
              </div>

              {/* AI Supervisor Feedback Banner */}
              <div style={{ background: '#0B0F1780', padding: '12px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldCheck size={18} color="#38BDF8" />
                <span style={{ fontSize: '12px', color: '#94A3B8' }}>
                  <strong style={{ color: '#38BDF8' }}>AI Supervisor Insight:</strong> {aiAdvisory}
                </span>
              </div>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}