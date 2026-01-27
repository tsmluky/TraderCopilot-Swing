export interface PerformanceMetric {
    token: string;
    timeframe: string;
    total_trades: number;
    win_rate: number;
    total_r: number;
    wins: number;
    losses: number;
    period_label: string; // e.g. "5 Years", "2 Years", "6 Months"
}

export const PERFORMANCE_HISTORY: Record<string, PerformanceMetric[]> = {
    // Strategy ID: trend_following_native_v1
    "trend_following_native_v1": [
        { token: "BTC", timeframe: "1h", total_trades: 406, win_rate: 35.7, total_r: -15.6, wins: 145, losses: 261, period_label: "5 Years" },
        { token: "BTC", timeframe: "4h", total_trades: 88, win_rate: 45.5, total_r: 19.7, wins: 40, losses: 48, period_label: "5 Years" },
        { token: "ETH", timeframe: "1h", total_trades: 363, win_rate: 37.2, total_r: 0.5, wins: 135, losses: 228, period_label: "5 Years" },
        { token: "ETH", timeframe: "4h", total_trades: 106, win_rate: 46.2, total_r: 25.9, wins: 49, losses: 57, period_label: "5 Years" },
        { token: "SOL", timeframe: "1h", total_trades: 307, win_rate: 44.6, total_r: 61.8, wins: 137, losses: 170, period_label: "5 Years" },
        { token: "SOL", timeframe: "4h", total_trades: 86, win_rate: 53.5, total_r: 37.8, wins: 46, losses: 40, period_label: "5 Years" },
        { token: "BNB", timeframe: "1h", total_trades: 337, win_rate: 37.4, total_r: 2.2, wins: 126, losses: 211, period_label: "5 Years" },
        { token: "BNB", timeframe: "4h", total_trades: 93, win_rate: 31.2, total_r: -14.9, wins: 29, losses: 64, period_label: "5 Years" },
        { token: "XRP", timeframe: "1h", total_trades: 365, win_rate: 34.2, total_r: -28.5, wins: 125, losses: 240, period_label: "5 Years" },
        { token: "XRP", timeframe: "4h", total_trades: 88, win_rate: 38.6, total_r: 3.5, wins: 34, losses: 54, period_label: "5 Years" },
    ],

    // Strategy ID: donchian_v2
    "donchian_v2": [
        { token: "BTC", timeframe: "1h", total_trades: 1441, win_rate: 36.7, total_r: -30.3, wins: 529, losses: 912, period_label: "5 Years" },
        { token: "BTC", timeframe: "4h", total_trades: 330, win_rate: 40.6, total_r: 27.3, wins: 134, losses: 196, period_label: "5 Years" },
        { token: "ETH", timeframe: "1h", total_trades: 1527, win_rate: 38.4, total_r: 38.3, wins: 587, losses: 940, period_label: "5 Years" },
        { token: "ETH", timeframe: "4h", total_trades: 343, win_rate: 42.0, total_r: 41.0, wins: 144, losses: 199, period_label: "5 Years" },
        { token: "SOL", timeframe: "1h", total_trades: 1869, win_rate: 39.8, total_r: 115.0, wins: 744, losses: 1125, period_label: "5 Years" },
        { token: "SOL", timeframe: "4h", total_trades: 407, win_rate: 40.0, total_r: 27.7, wins: 163, losses: 244, period_label: "5 Years" },
        { token: "BNB", timeframe: "1h", total_trades: 1657, win_rate: 38.3, total_r: 36.3, wins: 635, losses: 1022, period_label: "5 Years" },
        { token: "BNB", timeframe: "4h", total_trades: 437, win_rate: 43.0, total_r: 64.3, wins: 188, losses: 249, period_label: "5 Years" },
        { token: "XRP", timeframe: "1h", total_trades: 1453, win_rate: 39.3, total_r: 69.7, wins: 571, losses: 882, period_label: "5 Years" },
        { token: "XRP", timeframe: "4h", total_trades: 312, win_rate: 42.9, total_r: 45.3, wins: 134, losses: 178, period_label: "5 Years" },
    ],

    // Strategy ID: mean_reversion_v1 (Simulated Baseline)
    "mean_reversion_v1": [
        { token: "BTC", timeframe: "1h", total_trades: 850, win_rate: 62.5, total_r: 45.2, wins: 531, losses: 319, period_label: "5 Years" },
        { token: "BTC", timeframe: "4h", total_trades: 210, win_rate: 68.1, total_r: 32.5, wins: 143, losses: 67, period_label: "5 Years" },
        { token: "ETH", timeframe: "1h", total_trades: 920, win_rate: 60.2, total_r: 38.0, wins: 554, losses: 366, period_label: "5 Years" },
        { token: "ETH", timeframe: "4h", total_trades: 235, win_rate: 65.5, total_r: 29.8, wins: 154, losses: 81, period_label: "5 Years" },
        { token: "SOL", timeframe: "1h", total_trades: 1100, win_rate: 58.5, total_r: 55.4, wins: 643, losses: 457, period_label: "5 Years" },
        { token: "SOL", timeframe: "4h", total_trades: 280, win_rate: 63.8, total_r: 42.1, wins: 178, losses: 102, period_label: "5 Years" },
        { token: "BNB", timeframe: "1h", total_trades: 780, win_rate: 61.0, total_r: 28.5, wins: 476, losses: 304, period_label: "5 Years" },
        { token: "BNB", timeframe: "4h", total_trades: 195, win_rate: 66.2, total_r: 22.0, wins: 129, losses: 66, period_label: "5 Years" },
        { token: "XRP", timeframe: "1h", total_trades: 810, win_rate: 59.8, total_r: 31.2, wins: 484, losses: 326, period_label: "5 Years" },
        { token: "XRP", timeframe: "4h", total_trades: 205, win_rate: 64.5, total_r: 25.4, wins: 132, losses: 73, period_label: "5 Years" },
    ]
};
