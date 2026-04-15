import { useState } from "react";
import { Sprout, User, Lock, ArrowRight } from "lucide-react";

interface LoginProps {
  onLogin: () => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState<"en" | "hi">("en");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Dummy login - any credentials work
    if (mobile && password) {
      onLogin();
    }
  };

  const content = {
    en: {
      title: "Market Price Shock Predictor",
      subtitle: "Smart Price Alerts for Farmers",
      welcome: "Welcome Back",
      description:
        "Login to access your personalized market insights",
      mobilePlaceholder: "Mobile Number",
      passwordPlaceholder: "Password",
      loginButton: "Login",
      demoNote:
        "Demo Login: Use any mobile number and password",
      features: [
        "Early warning for price drops",
        "Real-time market analysis",
        "Smart recommendations",
      ],
    },
    hi: {
      title: "बाजार मूल्य शॉक भविष्यवक्ता",
      subtitle: "किसानों के लिए स्मार्ट मूल्य अलर्ट",
      welcome: "स्वागत है",
      description:
        "अपने व्यक्तिगत बाजार जानकारी के लिए लॉगिन करें",
      mobilePlaceholder: "मोबाइल नंबर",
      passwordPlaceholder: "पासवर्ड",
      loginButton: "लॉगिन करें",
      demoNote:
        "डेमो लॉगिन: कोई भी मोबाइल नंबर और पासवर्ड उपयोग करें",
      features: [
        "मूल्य गिरावट की पूर्व चेतावनी",
        "रीयल-टाइम बाजार विश्लेषण",
        "स्मार्ट सिफारिशें",
      ],
    },
  };

  const t = content[language];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-green-50 flex items-center justify-center p-4">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left Side - Branding & Features */}
        <div className="hidden lg:block">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-green-200 shadow-xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-green-600 text-white p-4 rounded-xl">
                <Sprout size={40} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {t.title}
                </h1>
                <p className="text-sm text-gray-600">
                  {t.subtitle}
                </p>
              </div>
            </div>

            <div className="space-y-6 mt-8">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  {language === "en"
                    ? "Why Use This System?"
                    : "इस प्रणाली का उपयोग क्यों करें?"}
                </h2>
                <div className="space-y-3">
                  {t.features.map((feature, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-3"
                    >
                      <div className="bg-green-100 text-green-700 p-2 rounded-lg mt-0.5">
                        <ArrowRight size={16} />
                      </div>
                      <p className="text-gray-700">{feature}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-6 border-t border-gray-200">
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">
                    8+
                  </p>
                  <p className="text-xs text-gray-600">
                    {language === "en" ? "Crops" : "फसलें"}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">
                    6+
                  </p>
                  <p className="text-xs text-gray-600">
                    {language === "en" ? "Markets" : "बाजार"}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-orange-600">
                    24/7
                  </p>
                  <p className="text-xs text-gray-600">
                    {language === "en"
                      ? "Monitoring"
                      : "निगरानी"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 lg:p-12 border border-gray-200">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="bg-green-600 text-white p-3 rounded-xl">
              <Sprout size={32} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {t.title}
              </h1>
              <p className="text-xs text-gray-600">
                {t.subtitle}
              </p>
            </div>
          </div>

          {/* Language Toggle */}
          <div className="flex justify-end mb-6">
            <div className="inline-flex rounded-lg border border-gray-300 p-1">
              <button
                onClick={() => setLanguage("en")}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  language === "en"
                    ? "bg-green-600 text-white"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage("hi")}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  language === "hi"
                    ? "bg-green-600 text-white"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                हिंदी
              </button>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {t.welcome}
            </h2>
            <p className="text-gray-600">{t.description}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Mobile Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {language === "en"
                  ? "Mobile Number"
                  : "मोबाइल नंबर"}
              </label>
              <div className="relative">
                <User
                  size={20}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                />
                <input
                  type="tel"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  placeholder={t.mobilePlaceholder}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-lg"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {language === "en" ? "Password" : "पासवर्ड"}
              </label>
              <div className="relative">
                <Lock
                  size={20}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t.passwordPlaceholder}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-lg"
                  required
                />
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2 text-lg"
            >
              {t.loginButton}
              <ArrowRight size={20} />
            </button>
          </form>

          {/* Demo Note */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800 text-center">
              {t.demoNote}
            </p>
          </div>

          {/* Additional Info */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              {language === "en"
                ? "Powered by SRM • Supported by Government of India"
                : "मशीन लर्निंग द्वारा संचालित • भारत सरकार द्वारा समर्थित"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}