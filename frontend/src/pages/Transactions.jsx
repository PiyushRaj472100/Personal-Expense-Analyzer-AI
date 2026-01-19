import { useState, useEffect } from 'react';
import { transactionsAPI } from '../services/api';
import { Plus, Trash2, MessageSquare, X, Check } from 'lucide-react';
import { format } from 'date-fns';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSMSModal, setShowSMSModal] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    category: '',
    source: 'manual',
  });
  const [customCategory, setCustomCategory] = useState('');
  const [smsText, setSmsText] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      const response = await transactionsAPI.getAll();
      setTransactions(response.data.transactions || []);
      setError('');
    } catch (err) {
      setError('Failed to load transactions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransaction = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate custom category if "Other" is selected
    if (formData.category === 'Other' && !customCategory.trim()) {
      setError('Please enter a category name when selecting "Other"');
      return;
    }

    try {
      const data = {
        ...formData,
        amount: parseFloat(formData.amount),
        // If "Other" is selected, use the custom category name
        category: formData.category === 'Other' ? customCategory.trim() : formData.category,
      };

      const response = await transactionsAPI.add(data);

      if (response.data.alert) {
        setSuccess(`Transaction added! ${response.data.alert}`);
      } else {
        setSuccess('Transaction added successfully!');
      }

      setFormData({
        title: '',
        amount: '',
        date: new Date().toISOString().split('T')[0],
        category: '',
        source: 'manual',
      });
      setCustomCategory('');
      setShowAddModal(false);
      fetchTransactions();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add transaction');
    }
  };

  const handleAddFromSMS = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await transactionsAPI.addFromSMS({ message: smsText });

      if (response.data.alert) {
        setSuccess(`Transaction added from SMS! ${response.data.alert}`);
      } else {
        setSuccess('Transaction added from SMS successfully!');
      }

      setSmsText('');
      setShowSMSModal(false);
      fetchTransactions();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse SMS');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) {
      return;
    }

    try {
      await transactionsAPI.delete(id);
      setSuccess('Transaction deleted successfully!');
      fetchTransactions();
    } catch (err) {
      setError('Failed to delete transaction');
    }
  };

  const categories = [
    'Food & Dining',
    'Food & Groceries',
    'Transportation',
    'Entertainment',
    'Healthcare',
    'Housing',
    'Utilities',
    'Shopping',
    'Technology',
    'Other',
  ];

  const sources = [
    { value: 'manual', label: 'Manual Entry' },
    { value: 'cash', label: 'Cash' },
    { value: 'upi', label: 'UPI' },
    { value: 'card', label: 'Card' },
    { value: 'netbanking', label: 'Net Banking' },
  ];

  return (
    <div className="space-y-6 flex-1">
      {/* Header */}
      <div className="glass-card w-full">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">

          <div className="w-full md:w-auto">
            <p className="pill-soft">Control every rupee</p>
            <h1 className="text-3xl font-extrabold text-ink mt-1">Transactions</h1>
            <p className="muted">Log, review, and parse SMS without touching the backend.</p>
          </div>

          <div className="w-full md:w-auto flex flex-col sm:flex-row flex-wrap gap-3">

            <button
              onClick={() => setShowSMSModal(true)}
              className="w-full sm:w-auto btn-secondary inline-flex items-center justify-center"
            >
              <MessageSquare className="mr-2 w-4 h-4" />
              Parse SMS
            </button>

            <button
              onClick={() => setShowAddModal(true)}
              className="w-full sm:w-auto btn-primary inline-flex items-center justify-center"
            >
              <Plus className="mr-2 w-4 h-4" />
              Add Transaction
            </button>

          </div>

        </div>
      </div>


      {/* Messages */}
      {error && (
        <div className="card border-2 border-red-400 bg-red-50">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}
      {success && (
        <div className="card border-2 border-green-500 bg-green-50">
          <p className="text-green-800 text-sm">{success}</p>
        </div>
      )}

      {/* Transactions List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      ) : transactions.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-ink/70 mb-4">No transactions yet</p>
          <button onClick={() => setShowAddModal(true)} className="btn-primary">
            Add Your First Transaction
          </button>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-ink/10">
              <thead className="bg-paper">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-bold text-ink uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-ink uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-ink uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-ink uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-ink uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-bold text-ink uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-ink/10">
                {transactions.map((transaction) => (
                  <tr key={transaction._id} className="hover:bg-primary-50/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-ink font-semibold">
                      {format(new Date(transaction.date), 'MMM dd, yyyy')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-ink">
                      {transaction.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center gap-2">
                        <span className="badge-outline bg-accent-teal/20 border-ink">
                          {transaction.category}
                        </span>
                        {transaction.is_anomaly && (
                          <span
                            className={`badge-outline text-xs ${
                              transaction.anomaly_severity === 'high'
                                ? 'bg-red-100 border-red-400 text-red-700'
                                : transaction.anomaly_severity === 'medium'
                                ? 'bg-yellow-100 border-yellow-400 text-yellow-700'
                                : 'bg-orange-100 border-orange-400 text-orange-700'
                            }`}
                            title="Anomaly detected"
                          >
                            ⚠️
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-ink/80">
                      {transaction.source}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-extrabold text-ink">
                      ₹{transaction.amount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleDelete(transaction._id)}
                        className="text-red-600 hover:text-red-900 p-2 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Transaction Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Add Transaction</h2>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setCustomCategory('');
                  setFormData({
                    title: '',
                    amount: '',
                    date: new Date().toISOString().split('T')[0],
                    category: '',
                    source: 'manual',
                  });
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddTransaction} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="input-field"
                  required
                  placeholder="e.g., Grocery Shopping"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount (₹)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="input-field"
                  required
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category (optional - will auto-detect)
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => {
                    setFormData({ ...formData, category: e.target.value });
                    // Clear custom category when switching away from "Other"
                    if (e.target.value !== 'Other') {
                      setCustomCategory('');
                    }
                  }}
                  className="input-field"
                >
                  <option value="">Auto-detect</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              {/* Custom Category Input - Show when "Other" is selected */}
              {formData.category === 'Other' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={customCategory}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    className="input-field"
                    required
                    placeholder="e.g., Gym Membership, Pet Care, etc."
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    💡 This helps our AI learn and categorize similar transactions in the future
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Payment Source
                </label>
                <select
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                  className="input-field"
                  required
                >
                  {sources.map((src) => (
                    <option key={src.value} value={src.value}>
                      {src.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary flex-1 inline-flex items-center justify-center">
                  <Check className="mr-2 w-4 h-4" />
                  Add
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* SMS Parser Modal */}
      {showSMSModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Parse SMS Transaction</h2>
              <button
                onClick={() => setShowSMSModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddFromSMS} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  SMS Message
                </label>
                <textarea
                  value={smsText}
                  onChange={(e) => setSmsText(e.target.value)}
                  className="input-field min-h-[150px]"
                  required
                  placeholder="Paste your banking SMS here..."
                />
                <p className="mt-1 text-xs text-gray-500">
                  Example: "INR 500.00 debited at GROCERY STORE on 01-01-2024"
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowSMSModal(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary flex-1 inline-flex items-center justify-center">
                  <MessageSquare className="mr-2 w-4 h-4" />
                  Parse & Add
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Transactions;