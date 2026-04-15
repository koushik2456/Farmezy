export type RiskLevel = "low" | "medium" | "high";

export interface Crop {
  id: string;
  name: string;
  nameHindi: string;
  currentPrice: number;
  unit: string;
  riskLevel: RiskLevel;
  priceChange: number;
  predictedShock: number;
  trend: "up" | "down" | "stable";
  season: string;
}

export interface Market {
  id: string;
  name: string;
  state: string;
  riskLevel: RiskLevel;
  highRiskCrops: number;
  totalCrops: number;
  averagePriceChange: number;
}

export interface Alert {
  id: string;
  crop: string;
  market: string;
  riskLevel: RiskLevel;
  message: string;
  date: string;
  isRead: boolean;
  recommendation: string;
}

export interface PriceData {
  date: string;
  price: number;
  predicted?: number;
  shockProbability?: number;
}

export const crops: Crop[] = [
  {
    id: "1",
    name: "Wheat",
    nameHindi: "गेहूं",
    currentPrice: 2150,
    unit: "₹/quintal",
    riskLevel: "low",
    priceChange: 2.5,
    predictedShock: 15,
    trend: "up",
    season: "Rabi"
  },
  {
    id: "2",
    name: "Rice",
    nameHindi: "चावल",
    currentPrice: 3200,
    unit: "₹/quintal",
    riskLevel: "medium",
    priceChange: -3.2,
    predictedShock: 45,
    trend: "down",
    season: "Kharif"
  },
  {
    id: "3",
    name: "Onion",
    nameHindi: "प्याज",
    currentPrice: 1800,
    unit: "₹/quintal",
    riskLevel: "high",
    priceChange: -12.5,
    predictedShock: 75,
    trend: "down",
    season: "Rabi & Kharif"
  },
  {
    id: "4",
    name: "Tomato",
    nameHindi: "टमाटर",
    currentPrice: 2500,
    unit: "₹/quintal",
    riskLevel: "high",
    priceChange: -15.8,
    predictedShock: 82,
    trend: "down",
    season: "Kharif"
  },
  {
    id: "5",
    name: "Potato",
    nameHindi: "आलू",
    currentPrice: 1200,
    unit: "₹/quintal",
    riskLevel: "low",
    priceChange: 1.8,
    predictedShock: 20,
    trend: "stable",
    season: "Rabi"
  },
  {
    id: "6",
    name: "Cotton",
    nameHindi: "कपास",
    currentPrice: 6500,
    unit: "₹/quintal",
    riskLevel: "medium",
    priceChange: -5.5,
    predictedShock: 50,
    trend: "down",
    season: "Kharif"
  },
  {
    id: "7",
    name: "Soybean",
    nameHindi: "सोयाबीन",
    currentPrice: 4200,
    unit: "₹/quintal",
    riskLevel: "low",
    priceChange: 3.2,
    predictedShock: 18,
    trend: "up",
    season: "Kharif"
  },
  {
    id: "8",
    name: "Sugarcane",
    nameHindi: "गन्ना",
    currentPrice: 310,
    unit: "₹/quintal",
    riskLevel: "low",
    priceChange: 0.5,
    predictedShock: 12,
    trend: "stable",
    season: "Year-round"
  },
];

export const markets: Market[] = [
  {
    id: "1",
    name: "Azadpur Mandi",
    state: "Delhi",
    riskLevel: "high",
    highRiskCrops: 3,
    totalCrops: 12,
    averagePriceChange: -8.5,
  },
  {
    id: "2",
    name: "Vashi APMC",
    state: "Maharashtra",
    riskLevel: "medium",
    highRiskCrops: 2,
    totalCrops: 15,
    averagePriceChange: -4.2,
  },
  {
    id: "3",
    name: "Koyambedu Market",
    state: "Tamil Nadu",
    riskLevel: "medium",
    highRiskCrops: 2,
    totalCrops: 18,
    averagePriceChange: -3.8,
  },
  {
    id: "4",
    name: "Lasalgaon Market",
    state: "Maharashtra",
    riskLevel: "high",
    highRiskCrops: 4,
    totalCrops: 8,
    averagePriceChange: -11.2,
  },
  {
    id: "5",
    name: "Binnypet Market",
    state: "Karnataka",
    riskLevel: "low",
    highRiskCrops: 1,
    totalCrops: 14,
    averagePriceChange: 1.5,
  },
  {
    id: "6",
    name: "Gaddiannaram Market",
    state: "Telangana",
    riskLevel: "low",
    highRiskCrops: 0,
    totalCrops: 10,
    averagePriceChange: 2.8,
  },
];

export const alerts: Alert[] = [
  {
    id: "1",
    crop: "Tomato",
    market: "Azadpur Mandi",
    riskLevel: "high",
    message: "High price shock risk detected for Tomato in next 7 days",
    date: "2026-02-23",
    isRead: false,
    recommendation: "Consider storing produce or selling in nearby markets with better prices",
  },
  {
    id: "2",
    crop: "Onion",
    market: "Lasalgaon Market",
    riskLevel: "high",
    message: "Sudden supply increase expected - price drop likely",
    date: "2026-02-23",
    isRead: false,
    recommendation: "Sell immediately or arrange cold storage facilities",
  },
  {
    id: "3",
    crop: "Rice",
    market: "Vashi APMC",
    riskLevel: "medium",
    message: "Moderate price fluctuation expected due to seasonal factors",
    date: "2026-02-22",
    isRead: true,
    recommendation: "Monitor market for next 3-4 days before making selling decision",
  },
  {
    id: "4",
    crop: "Cotton",
    market: "Azadpur Mandi",
    riskLevel: "medium",
    message: "Weather conditions may affect prices in coming week",
    date: "2026-02-22",
    isRead: true,
    recommendation: "Wait for weather stabilization or explore alternative markets",
  },
  {
    id: "5",
    crop: "Wheat",
    market: "Binnypet Market",
    riskLevel: "low",
    message: "Stable prices expected - good time to sell",
    date: "2026-02-21",
    isRead: true,
    recommendation: "Current market conditions are favorable for selling",
  },
];

// Generate price history data
export const generatePriceHistory = (
  basePrice: number,
  volatility: number,
  trend: "up" | "down" | "stable",
  shockDay?: number
): PriceData[] => {
  const data: PriceData[] = [];
  const days = 90; // 90 days history
  const futureDays = 14; // 14 days prediction
  
  let price = basePrice * 0.9;
  const trendFactor = trend === "up" ? 0.002 : trend === "down" ? -0.002 : 0;
  
  // Historical data
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    
    const dailyChange = (Math.random() - 0.5) * volatility;
    price = price * (1 + trendFactor + dailyChange);
    
    data.push({
      date: date.toISOString().split("T")[0],
      price: Math.round(price),
    });
  }
  
  // Future predictions
  const currentPrice = data[data.length - 1].price;
  price = currentPrice;
  
  for (let i = 1; i <= futureDays; i++) {
    const date = new Date();
    date.setDate(date.getDate() + i);
    
    let dailyChange = (Math.random() - 0.5) * volatility * 0.8;
    
    // Introduce shock if specified
    if (shockDay && i === shockDay) {
      dailyChange = -0.15; // 15% drop
    }
    
    price = price * (1 + trendFactor + dailyChange);
    
    const shockProb = shockDay && i >= shockDay - 2 && i <= shockDay + 2
      ? 60 + Math.random() * 30
      : Math.random() * 40;
    
    data.push({
      date: date.toISOString().split("T")[0],
      predicted: Math.round(price),
      shockProbability: Math.round(shockProb),
    });
  }
  
  return data;
};
