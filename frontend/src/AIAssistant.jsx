import { useState } from "react";

function AIAssistant({ onBookAppointment }) {
  const [symptoms, setSymptoms] = useState([]);
  const [currentInput, setCurrentInput] = useState("");
  const [chatMessages, setChatMessages] = useState([
    {
      type: "bot",
      text: "👋 Hello! I'm your AI Health Assistant. What symptoms are you experiencing today?",
    },
  ]);
  const [showBooking, setShowBooking] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const commonSymptoms = [
    "Chest pain",
    "Breathing difficulty",
    "High fever",
    "Cough",
    "Headache",
    "Vomiting",
    "Cold",
  ];

  const handleAddSymptom = (symptom) => {
    if (!symptoms.includes(symptom)) {
      setSymptoms([...symptoms, symptom]);
      setChatMessages([
        ...chatMessages,
        { type: "user", text: symptom },
      ]);
      setIsTyping(true);
      setTimeout(() => {
        setChatMessages(prev => [
          ...prev,
          {
            type: "bot",
            text: `✓ Added: ${symptom}. Anything else? You can select more symptoms or type your own.`,
          },
        ]);
        setIsTyping(false);
      }, 800);
      setCurrentInput("");
    }
  };

  const handleCustomSymptom = () => {
    if (currentInput.trim()) {
      handleAddSymptom(currentInput.trim());
    }
  };

  const handleRemoveSymptom = (symptom) => {
    setSymptoms(symptoms.filter((s) => s !== symptom));
  };

  const calculateSeverity = () => {
    const severityMap = {
      "chest pain": 90,
      "breathing difficulty": 85,
      "high fever": 70,
      vomiting: 50,
      headache: 30,
      cough: 20,
      cold: 10,
    };

    let score = 0;
    symptoms.forEach((symptom) => {
      score += severityMap[symptom.toLowerCase()] || 5;
    });

    return Math.min(score, 100);
  };

  const handleProceedToBooking = () => {
    const severity = calculateSeverity();
    setChatMessages([
      ...chatMessages,
      { type: "user", text: "Ready to book appointment" },
    ]);
    setIsTyping(true);
    setTimeout(() => {
      setChatMessages(prev => [
        ...prev,
        {
          type: "bot",
          text: `Based on your symptoms, I assess your condition as requiring ${
            severity > 80 ? "🚨 urgent" : severity > 50 ? "📋 standard" : "✅ routine"
          } care. Let me connect you with an available doctor.`,
        },
      ]);
      setShowBooking(true);
      setIsTyping(false);
    }, 1000);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-3xl shadow-2xl w-full max-w-md border border-cyan-500 border-opacity-40 flex flex-col max-h-[90vh] animate-scale-up">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 p-6 rounded-t-3xl relative overflow-hidden">
          <div className="absolute inset-0 opacity-20 animate-blob"></div>
          <div className="relative z-10">
            <h2 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
              <span className="animate-float">🤖</span> 
              <span className="animate-text-glow">AI Health Assistant</span>
            </h2>
            <p className="text-cyan-100 text-sm font-medium">Describe your symptoms and let me help</p>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gradient-to-b from-slate-800 to-slate-900">
          {chatMessages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"} animate-slide-up`}
            >
              <div
                className={`max-w-xs px-4 py-3 rounded-2xl font-medium transition-all duration-300 ${
                  msg.type === "user"
                    ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg hover-glow"
                    : "bg-slate-700 text-gray-100 border border-cyan-500 border-opacity-30 backdrop-blur-sm"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        {/* Selected Symptoms */}
        {symptoms.length > 0 && (
          <div className="px-4 py-2 bg-gray-800 border-t border-gray-700">
            <p className="text-sm text-gray-400 mb-2">Selected Symptoms:</p>
            <div className="flex flex-wrap gap-2">
              {symptoms.map((symptom) => (
                <span
                  key={symptom}
                  className="bg-purple-600 text-white text-xs px-3 py-1 rounded-full flex items-center gap-2"
                >
                  {symptom}
                  <button
                    onClick={() => handleRemoveSymptom(symptom)}
                    className="hover:text-red-300"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {!showBooking ? (
          <>
            {/* Quick Symptom Buttons */}
            <div className="px-4 py-3 border-t border-gray-700">
              <p className="text-xs text-gray-400 mb-2">Common Symptoms:</p>
              <div className="grid grid-cols-2 gap-2">
                {commonSymptoms.map((symptom) => (
                  <button
                    key={symptom}
                    onClick={() => handleAddSymptom(symptom)}
                    disabled={symptoms.includes(symptom)}
                    className={`text-xs p-2 rounded-lg transition ${
                      symptoms.includes(symptom)
                        ? "bg-gray-700 text-gray-500 opacity-50"
                        : "bg-gray-800 hover:bg-purple-600 text-white border border-gray-700"
                    }`}
                  >
                    {symptom}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Input */}
            <div className="px-4 py-3 border-t border-gray-700 flex gap-2">
              <input
                type="text"
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleCustomSymptom()}
                placeholder="Type other symptom..."
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none"
              />
              <button
                onClick={handleCustomSymptom}
                className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg transition"
              >
                Add
              </button>
            </div>

            {/* Action Buttons */}
            <div className="px-4 py-3 border-t border-gray-700 flex gap-2">
              {symptoms.length > 0 && (
                <button
                  onClick={handleProceedToBooking}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-2 rounded-lg transition"
                >
                  📅 Proceed to Booking
                </button>
              )}
            </div>
          </>
        ) : (
          <div className="px-4 py-4 border-t border-gray-700">
            <button
              onClick={() => onBookAppointment(symptoms)}
              className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold py-3 rounded-lg transition"
            >
              📋 Book Appointment Now
            </button>
            <button
              onClick={() => window.location.href = "/patient"}
              className="w-full bg-gray-800 hover:bg-gray-700 text-white font-semibold py-2 rounded-lg transition mt-2"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default AIAssistant;
