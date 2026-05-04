import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, RefreshCcw, Download, CheckCircle, AlertCircle, Loader2, CreditCard } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:5000/generate';

function App() {
  const [formData, setFormData] = useState({
    company: '',
    name: '',
    department: '',
    gender: 'Male',
    phone: '',
    address: ''
  });
  const [image, setImage] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [cameraActive, setCameraActive] = useState(true);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (cameraActive && !result) {
      startCamera();
    }
  }, [cameraActive, result]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError("Camera access denied. Please check permissions.");
    }
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (video && canvas) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      const dataUrl = canvas.toDataURL('image/jpeg');
      setImage(dataUrl);
      setCameraActive(false);
      // Stop stream
      const stream = video.srcObject;
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    }
  };

  const retakePhoto = () => {
    setImage(null);
    setCameraActive(true);
    setResult(null);
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setError("Please capture a photo first.");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await axios.post(API_URL, {
        ...formData,
        image: image
      });

      if (response.data.success) {
        setResult(response.data);
      } else {
        setError(response.data.error || "Failed to generate ID card.");
      }
    } catch (err) {
      setError("Backend connection failed. Is the server running?");
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadImage = (base64, filename) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${base64}`;
    link.download = filename;
    link.click();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-500/30">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <header className="text-center mb-16">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center gap-3 mb-4"
          >
            <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-600/20">
              <CreditCard size={32} className="text-white" />
            </div>
            <h1 className="text-4xl font-black tracking-tight">ID<span className="text-blue-500">PRO</span></h1>
          </motion.div>
          <p className="text-slate-400 text-lg">Next-generation professional ID card generator.</p>
        </header>

        <main className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left Side: Form & Camera */}
          <motion.section 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-8"
          >
            <div className="glass-panel p-8 rounded-3xl border border-slate-800 bg-slate-900/50 backdrop-blur-xl">
              <div className="relative mb-8 overflow-hidden rounded-2xl bg-black aspect-video border-2 border-slate-800 group">
                {cameraActive && !image ? (
                  <>
                    <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      <div className="w-1/2 h-2/3 border-2 border-dashed border-white/30 rounded-2xl"></div>
                    </div>
                    <button 
                      onClick={capturePhoto}
                      className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-white text-black px-6 py-3 rounded-full font-bold flex items-center gap-2 hover:scale-105 transition-transform shadow-2xl"
                    >
                      <Camera size={20} /> Capture Photo
                    </button>
                  </>
                ) : (
                  <div className="relative w-full h-full">
                    {image && <img src={image} className="w-full h-full object-cover" alt="Captured" />}
                    <button 
                      onClick={retakePhoto}
                      className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-slate-800/80 backdrop-blur-md text-white px-6 py-3 rounded-full font-bold flex items-center gap-2 hover:bg-slate-700 transition-colors"
                    >
                      <RefreshCcw size={20} /> Retake
                    </button>
                  </div>
                )}
                <canvas ref={canvasRef} className="hidden" />
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-400 ml-1">Company</label>
                    <input 
                      type="text" name="company" required placeholder="Acme Corp"
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                      onChange={handleInputChange} value={formData.company}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-400 ml-1">Full Name</label>
                    <input 
                      type="text" name="name" required placeholder="John Doe"
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                      onChange={handleInputChange} value={formData.name}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-400 ml-1">Department</label>
                    <input 
                      type="text" name="department" placeholder="Engineering"
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                      onChange={handleInputChange} value={formData.department}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-400 ml-1">Gender</label>
                    <select 
                      name="gender"
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all appearance-none"
                      onChange={handleInputChange} value={formData.gender}
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-400 ml-1">Phone</label>
                  <input 
                    type="tel" name="phone" placeholder="+1 (555) 000-0000"
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                    onChange={handleInputChange} value={formData.phone}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-slate-400 ml-1">Address</label>
                  <textarea 
                    name="address" rows="2" placeholder="123 Silicon Valley, CA"
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all resize-none"
                    onChange={handleInputChange} value={formData.address}
                  />
                </div>

                <button 
                  type="submit" 
                  disabled={isGenerating}
                  className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white py-4 rounded-xl font-bold text-lg shadow-xl shadow-blue-600/20 transition-all flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <><Loader2 className="animate-spin" /> Processing...</>
                  ) : (
                    "Generate ID Card"
                  )}
                </button>
              </form>

              {error && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl flex items-center gap-3 text-red-400"
                >
                  <AlertCircle size={20} />
                  <p className="text-sm font-medium">{error}</p>
                </motion.div>
              )}
            </div>
          </motion.section>

          {/* Right Side: Preview */}
          <motion.section 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="sticky top-12"
          >
            <AnimatePresence mode="wait">
              {!result ? (
                <motion.div 
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-[600px] border-2 border-dashed border-slate-800 rounded-3xl flex flex-col items-center justify-center text-center p-12 text-slate-500"
                >
                  <CreditCard size={64} className="mb-6 opacity-20" />
                  <h3 className="text-xl font-bold text-slate-400 mb-2">Awaiting Data</h3>
                  <p className="max-w-xs">Fill out the form and capture a photo to generate your professional ID card preview.</p>
                </motion.div>
              ) : (
                <motion.div 
                  key="result"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-8"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                      <CheckCircle className="text-green-500" size={24} /> Preview Ready
                    </h3>
                    <button 
                      onClick={() => setResult(null)}
                      className="text-sm font-semibold text-blue-500 hover:text-blue-400"
                    >
                      Reset Form
                    </button>
                  </div>

                  <div className="space-y-8">
                    <div className="card-group">
                      <div className="flex items-center justify-between mb-3 px-1">
                        <span className="text-xs font-bold text-slate-500 tracking-widest uppercase">Front View</span>
                        <button 
                          onClick={() => downloadImage(result.front, `${formData.name}_Front.png`)}
                          className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors"
                        >
                          <Download size={18} />
                        </button>
                      </div>
                      <img 
                        src={`data:image/png;base64,${result.front}`} 
                        className="w-full rounded-2xl shadow-2xl shadow-black/50 border border-slate-800"
                        alt="ID Front" 
                      />
                    </div>

                    <div className="card-group">
                      <div className="flex items-center justify-between mb-3 px-1">
                        <span className="text-xs font-bold text-slate-500 tracking-widest uppercase">Back View</span>
                        <button 
                          onClick={() => downloadImage(result.back, `${formData.name}_Back.png`)}
                          className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors"
                        >
                          <Download size={18} />
                        </button>
                      </div>
                      <img 
                        src={`data:image/png;base64,${result.back}`} 
                        className="w-full rounded-2xl shadow-2xl shadow-black/50 border border-slate-800"
                        alt="ID Back" 
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.section>
        </main>

        <footer className="mt-24 text-center text-slate-500 text-sm">
          <p>&copy; 2026 ID Pro Generator System. Built for excellence.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
