import { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  IndianRupee,
  AlertTriangle,
  Lightbulb,
  ArrowUpRight,
  ArrowDownRight,
  X,
  Info,
  CheckCircle,
  AlertCircle,
  Zap
} from 'lucide-react';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAnomalyPopup, setShowAnomalyPopup] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  useEffect(() => {
    // Show anomaly popup if there are urgent anomalies
    if (data && data.urgent_anomalies && data.urgent_anomalies.length > 0) {
      // Check if user has already dismissed this session
      const dismissed = sessionStorage.getItem('anomaly_popup_dismissed');
      if (!dismissed) {
        setShowAnomalyPopup(true);
      }
    }
  }, [data]);

  const fetchDashboard = async () => {
    try {
      const response = await dashboardAPI.getDashboard();
      setData(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDismissPopup = () => {
    setShowAnomalyPopup(false);
    sessionStorage.setItem('anomaly_popup_dismissed', 'true');
    // Reset after 1 hour
    setTimeout(() => {
      sessionStorage.removeItem('anomaly_popup_dismissed');
    }, 3600000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="card text-center py-12">
        <p className="text-red-600">{error || 'No data available'}</p>
      </div>
    );
  }

  const getHealthScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getTipIcon = (severity, category) => {
    if (severity === 'high' || category === 'warning') return <AlertCircle className="w-5 h-5 text-red-500" />;
    if (severity === 'medium' || category === 'advice') return <Info className="w-5 h-5 text-blue-500" />;
    return <CheckCircle className="w-5 h-5 text-green-500" />;
  };

  const getTipBorderColor = (severity, category) => {
    if (severity === 'high' || category === 'warning') return 'border-red-200 bg-red-50/50';
    if (severity === 'medium' || category === 'advice') return 'border-blue-200 bg-blue-50/50';
    return 'border-green-200 bg-green-50/50';
  };

  return (
    <div className="space-y-6">
      {/* Anomaly Notification Popup */}
      {showAnomalyPopup && data.urgent_anomalies && data.urgent_anomalies.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border-4 border-red-300 animate-pulse-once">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-red-100 rounded-full">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-red-900">⚠️ Urgent Financial Alert</h3>
                  <p className="text-sm text-red-700">Anomalies detected in your spending</p>
                </div>
              </div>
              <button
                onClick={handleDismissPopup}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-3 mb-4">
              {data.urgent_anomalies.slice(0, 3).map((anomaly, index) => (
                <div key={index} className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-red-900">{anomaly.category}</span>
                    <span className="text-lg font-bold text-red-600">
                      ₹{anomaly.amount.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <p className="text-sm text-red-700">{anomaly.reason}</p>
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleDismissPopup}
                className="flex-1 btn-secondary"
              >
                I'll Review Later
              </button>
              <Link
                to="/transactions"
                onClick={handleDismissPopup}
                className="flex-1 btn-primary text-center"
              >
                View Details
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Hero Header */}
      <div className="glass-card">
        <div className="section-title">
          <div>
            <p className="pill-soft">Live finances</p>
            <h1 className="text-3xl font-extrabold mt-2 text-ink">Dashboard</h1>
            <p className="muted mt-1">Bold, honest money overview powered by your real data.</p>
          </div>
          <div className="flex items-center gap-3">
            {data.unread_anomalies_count > 0 && (
              <div className="relative">
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold animate-pulse">
                  {data.unread_anomalies_count}
                </div>
                <AlertTriangle className="w-6 h-6 text-red-500" />
              </div>
            )}
            <Link to="/transactions" className="btn-primary inline-flex items-center">
              Add Transaction
              <ArrowUpRight className="ml-2 w-4 h-4" />
            </Link>
          </div>
        </div>

        <div className="divider" />

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card bg-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="muted">Monthly Income</p>
                <p className="text-3xl font-bold text-ink mt-1">
                  ₹{data.income?.toLocaleString('en-IN', { maximumFractionDigits: 0 }) || 0}
                </p>
              </div>
              <div className="p-3 bg-primary-100 rounded-brutal border-2 border-ink shadow-brutal-sm">
                <TrendingUp className="w-6 h-6 text-primary-700" />
              </div>
            </div>
          </div>

          <div className="card bg-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="muted">Total Expenses</p>
                <p className="text-3xl font-bold text-red-600 mt-1">
                  ₹{data.expenses?.toLocaleString('en-IN', { maximumFractionDigits: 0 }) || 0}
                </p>
              </div>
              <div className="p-3 bg-accent-pink/30 rounded-brutal border-2 border-ink shadow-brutal-sm">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>

          <div className="card bg-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="muted">Savings</p>
                <p className={`text-3xl font-bold ${data.savings >= 0 ? 'text-green-600' : 'text-red-600'} mt-1`}>
                  ₹{Math.abs(data.savings || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </p>
                <p className="text-xs text-ink/70 mt-1">
                  {data.savings_percentage?.toFixed(1) || 0}% of income
                </p>
              </div>
              <div className={`p-3 rounded-brutal border-2 border-ink shadow-brutal-sm ${data.savings >= 0 ? 'bg-green-100' : 'bg-red-50'}`}>
                <IndianRupee className={`w-6 h-6 ${data.savings >= 0 ? 'text-green-700' : 'text-red-600'}`} />
              </div>
            </div>
          </div>

          <div className={`card bg-white border-2 ${getHealthScoreColor(data.health_score || 0)}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="muted">Health Score</p>
                <p className={`text-3xl font-bold mt-1 ${getHealthScoreColor(data.health_score || 0).split(' ')[0]}`}>
                  {data.health_score || 0}/100
                </p>
                <p className="text-xs text-ink/70 mt-1">
                  {data.health_score >= 80 ? 'Excellent' : data.health_score >= 60 ? 'Good' : 'Needs Attention'}
                </p>
              </div>
              <div className={`p-3 rounded-brutal border-2 border-ink shadow-brutal-sm ${getHealthScoreColor(data.health_score || 0).split(' ')[2]}`}>
                <Zap className={`w-6 h-6 ${getHealthScoreColor(data.health_score || 0).split(' ')[0]}`} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Categories & Recent Transactions */}
      <div className="section-grid">
        {/* Top Categories */}
        <div className="card">
          <div className="section-title">
            <h2 className="text-lg font-bold text-ink">Top Categories</h2>
            <span className="badge-outline">Where money is loudest</span>
          </div>
          {data.top_categories && data.top_categories.length > 0 ? (
            <div className="space-y-4">
              {data.top_categories.map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-semibold text-ink">{category.name}</span>
                      <span className="text-sm font-bold text-ink">
                        ₹{category.amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                      </span>
                    </div>
                    <div className="w-full bg-ink/10 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full transition-all"
                        style={{
                          width: `${(category.amount / data.expenses) * 100}%`,
                          maxWidth: '100%',
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink/60 text-center py-4">No categories yet</p>
          )}
        </div>

        {/* Recent Transactions */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="muted">Latest activity</p>
              <h2 className="text-lg font-bold text-ink">Recent Transactions</h2>
            </div>
            <Link to="/transactions" className="text-sm font-semibold text-primary-700 hover:text-primary-800 underline">
              View all
            </Link>
          </div>
          {data.recent_transactions && data.recent_transactions.length > 0 ? (
            <div className="space-y-3">
              {data.recent_transactions.map((transaction) => (
                <div
                  key={transaction._id}
                  className="flex items-center justify-between p-3 bg-paper rounded-brutal border-2 border-ink/10 hover:border-ink/40 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-ink">{transaction.title}</p>
                      {transaction.is_anomaly && (
                        <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-semibold">
                          Anomaly
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-ink/70">
                      {transaction.category} • {format(new Date(transaction.date), 'MMM dd, yyyy')}
                    </p>
                  </div>
                  <p className="text-sm font-bold text-ink">
                    ₹{transaction.amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink/60 text-center py-4">No transactions yet</p>
          )}
        </div>
      </div>

      {/* Anomalies Alert Section */}
      {data.anomalies && data.anomalies.length > 0 && (
        <div className="card border-4 border-red-300 bg-gradient-to-br from-red-50 to-orange-50 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="p-4 bg-red-100 rounded-full">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-red-900 mb-1">⚠️ Spending Anomalies Detected</h3>
                  <p className="text-sm text-red-700">Review these unusual spending patterns to maintain financial stability</p>
                </div>
                {data.unread_anomalies_count > 0 && (
                  <span className="px-3 py-1 bg-red-500 text-white rounded-full text-sm font-bold animate-pulse">
                    {data.unread_anomalies_count} New
                  </span>
                )}
              </div>
              <div className="space-y-3">
                {data.anomalies.slice(0, 3).map((anomaly, index) => (
                  <div key={index} className="p-4 bg-white rounded-xl border-2 border-red-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-bold text-red-900">{anomaly.category}</span>
                          <span
                            className={`text-xs px-2 py-1 rounded-full font-semibold ${
                              anomaly.severity === 'high'
                                ? 'bg-red-200 text-red-800'
                                : 'bg-yellow-200 text-yellow-800'
                            }`}
                          >
                            {anomaly.severity}
                          </span>
                        </div>
                        <p className="text-sm text-red-700 mb-2">{anomaly.reason}</p>
                        <p className="text-xs text-ink/60">Date: {anomaly.date ? format(new Date(anomaly.date), 'MMM dd, yyyy') : 'N/A'}</p>
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-2xl font-bold text-red-600">
                          ₹{anomaly.amount.toLocaleString('en-IN')}
                        </p>
                        <p className="text-xs text-ink/60">Score: {anomaly.score.toFixed(2)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {data.anomalies.length > 3 && (
                <Link
                  to="/transactions"
                  className="mt-4 inline-block text-sm font-semibold text-red-700 hover:text-red-900 underline"
                >
                  View all {data.anomalies.length} anomalies →
                </Link>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Regular Alerts */}
      {data.alerts && data.alerts.length > 0 && (
        <div className="card border-2 border-yellow-400 bg-yellow-50">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-700 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-bold text-yellow-900 mb-2">Alerts</h3>
              <div className="space-y-2">
                {data.alerts.map((alert, index) => (
                  <p key={index} className="text-sm text-yellow-800">
                    {alert.message}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Tips Section */}
      {data.tips && data.tips.length > 0 && (
        <div className="card bg-gradient-to-br from-primary-50 via-white to-accent-teal/20 border-2 border-primary-200 shadow-lg">
          <div className="flex items-start gap-4 mb-6">
            <div className="p-3 bg-primary-100 rounded-full">
              <Lightbulb className="w-7 h-7 text-primary-700" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-ink mb-1">💡 Personalized Financial Tips</h3>
              <p className="text-sm text-ink/70">
                {data.user_profile?.family_size > 1 
                  ? `Tailored advice for your family of ${data.user_profile.family_size}`
                  : 'AI-powered insights to improve your financial health'
                }
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.tips.map((tip, index) => (
              <div
                key={index}
                className={`p-5 rounded-xl border-2 ${getTipBorderColor(tip.severity, tip.category)} shadow-sm hover:shadow-md transition-all transform hover:-translate-y-1`}
              >
                <div className="flex items-start gap-3 mb-3">
                  {getTipIcon(tip.severity, tip.category)}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-semibold ${
                          tip.severity === 'high'
                            ? 'bg-red-100 text-red-700'
                            : tip.severity === 'medium'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {tip.severity === 'high' ? '🔴 High Priority' : tip.severity === 'medium' ? '🟡 Medium Priority' : '🟢 Low Priority'}
                      </span>
                      {tip.is_anomaly_tip && (
                        <span className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded-full font-semibold">
                          Anomaly Alert
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <p className="text-sm leading-relaxed text-ink/90 whitespace-pre-line">
                  {tip.message}
                </p>
                {tip.category && (
                  <div className="mt-3 pt-3 border-t border-ink/10">
                    <span className="text-xs text-ink/60 font-medium">
                      {tip.category === 'warning' ? '⚠️ Warning' : tip.category === 'advice' ? '💡 Actionable Advice' : '📊 Insight'}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
