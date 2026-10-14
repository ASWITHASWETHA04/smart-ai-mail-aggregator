import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Brain, 
  Database, 
  Cloud, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Mail, 
  Copy, 
  Download, 
  Check, 
  LogIn, 
  LogOut, 
  User as UserIcon, 
  Sliders,
  Send,
  BarChart3,
  Calendar,
  Clock,
  Coins,
  FileSpreadsheet,
  Filter,
  PieChart,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react';

interface BackendHealth {
  status: string;
  service: string;
  version: string;
  environment: string;
}

interface UserProfile {
  id: string;
  email: string;
  role: string;
}

interface GenerationOptions {
  categories: string[];
  tones: string[];
  lengths: string[];
  languages: string[];
}

interface EmailDraft {
  subject: string;
  body: string;
  category: string;
  tone: string;
  language: string;
  length: string;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  } | null;
}

interface AnalyticsSummary {
  total_events: number;
  successful_events: number;
  failed_events: number;
  success_rate: number | null;
  avg_duration_ms: number | null;
  median_duration_ms: number | null;
  total_tokens: number | null;
  avg_tokens: number | null;
  prompt_tokens_total: number | null;
  completion_tokens_total: number | null;
}

interface DailyActivityItem {
  date: string;
  total: number;
  successful: number;
  failed: number;
  success_rate: number | null;
  avg_duration_ms: number | null;
  total_tokens: number | null;
}

interface DistributionItem {
  label: string;
  count: number;
  percentage: number;
}

interface AnalyticsDistributions {
  categories: DistributionItem[];
  tones: DistributionItem[];
  languages: DistributionItem[];
  error_codes: DistributionItem[];
}

export const App: React.FC = () => {
  // Resolve API Base URL:
  // - In development mode (import.meta.env.DEV), default to local backend 'http://localhost:5000' if unspecified.
  // - In production/staging builds, use the build-time VITE_API_BASE_URL (never silent localhost fallback).
  const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL.trim() !== '')
    ? import.meta.env.VITE_API_BASE_URL.trim()
    : (import.meta.env.DEV ? 'http://localhost:5000' : '');

  // Navigation & View state
  const [activeTab, setActiveTab] = useState<'generator' | 'analytics' | 'overview'>('generator');
  
  // Health state
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);

  // Authentication state
  const [authToken, setAuthToken] = useState<string | null>(() => sessionStorage.getItem('smartmail_token'));
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authEmail, setAuthEmail] = useState<string>('');
  const [authPassword, setAuthPassword] = useState<string>('');
  const [authLoading, setAuthLoading] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // Options state
  const [options, setOptions] = useState<GenerationOptions>({
    categories: [
      'Academic communication',
      'Professional inquiry',
      'Job application',
      'Internship application',
      'Follow-up',
      'Meeting request',
      'Thank-you email',
      'Business proposal',
      'General professional email',
    ],
    tones: ['Professional', 'Formal', 'Friendly', 'Polite', 'Persuasive', 'Concise'],
    lengths: ['Short', 'Medium', 'Detailed'],
    languages: ['English', 'Spanish', 'French', 'German', 'Chinese', 'Hindi', 'Japanese'],
  });

  // Generator form state
  const [purpose, setPurpose] = useState<string>('');
  const [category, setCategory] = useState<string>('Academic communication');
  const [tone, setTone] = useState<string>('Formal');
  const [lengthPref, setLengthPref] = useState<string>('Medium');
  const [language, setLanguage] = useState<string>('English');
  const [recipient, setRecipient] = useState<string>('');
  const [keyPoints, setKeyPoints] = useState<string>('');
  const [additionalContext, setAdditionalContext] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);

  // Generation state
  const [generating, setGenerating] = useState<boolean>(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [currentDraft, setCurrentDraft] = useState<EmailDraft | null>(null);
  const [editableSubject, setEditableSubject] = useState<string>('');
  const [editableBody, setEditableBody] = useState<string>('');

  // Copy feedback states
  const [copiedSubject, setCopiedSubject] = useState<boolean>(false);
  const [copiedBody, setCopiedBody] = useState<boolean>(false);
  const [copiedFull, setCopiedFull] = useState<boolean>(false);

  // Analytics Dashboard state
  const [analyticsLoading, setAnalyticsLoading] = useState<boolean>(false);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [analyticsForbidden, setAnalyticsForbidden] = useState<boolean>(false);
  const [analyticsSummary, setAnalyticsSummary] = useState<AnalyticsSummary | null>(null);
  const [dailyActivity, setDailyActivity] = useState<DailyActivityItem[]>([]);
  const [analyticsDistributions, setAnalyticsDistributions] = useState<AnalyticsDistributions | null>(null);
  const [isAnalyticsEmpty, setIsAnalyticsEmpty] = useState<boolean>(false);
  
  // Date filters for analytics
  const todayStr = new Date().toISOString().split('T')[0];
  const thirtyDaysAgoStr = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  const [startDate, setStartDate] = useState<string>(thirtyDaysAgoStr);
  const [endDate, setEndDate] = useState<string>(todayStr);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [exportingCsv, setExportingCsv] = useState<boolean>(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  // Fetch backend health
  const checkHealth = async () => {
    setHealthLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/health`, { headers: { Accept: 'application/json' } });
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      } else {
        setHealth(null);
      }
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  };

  // Fetch options
  const fetchOptions = async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/email/options`);
      if (res.ok) {
        const data = await res.json();
        setOptions(data);
      }
    } catch {
      // Fallback options already initialized
    }
  };

  // Fetch current user if token exists
  const fetchCurrentUser = async (token: string) => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentUser(data.user);
      } else if (res.status === 401) {
        handleLogout();
      }
    } catch {
      // Keep session state
    }
  };

  useEffect(() => {
    checkHealth();
    fetchOptions();
    if (authToken) {
      fetchCurrentUser(authToken);
    }
  }, [authToken]);

  // Load analytics when switching to tab or changing filters
  const loadAnalyticsData = async () => {
    if (!authToken) {
      setAnalyticsForbidden(false);
      setAnalyticsError('Authentication required. Sign in with an administrator account to view telemetry.');
      return;
    }
    setAnalyticsLoading(true);
    setAnalyticsError(null);
    setAnalyticsForbidden(false);

    const queryParams = new URLSearchParams();
    if (startDate) queryParams.append('start_date', startDate);
    if (endDate) queryParams.append('end_date', endDate);
    if (selectedCategory && selectedCategory !== 'All') queryParams.append('category', selectedCategory);

    const qs = queryParams.toString() ? `?${queryParams.toString()}` : '';

    try {
      const headers = {
        Authorization: `Bearer ${authToken}`,
        Accept: 'application/json',
      };

      const [summaryRes, dailyRes, distRes] = await Promise.all([
        fetch(`${apiBaseUrl}/api/analytics/summary${qs}`, { headers }),
        fetch(`${apiBaseUrl}/api/analytics/daily${qs}`, { headers }),
        fetch(`${apiBaseUrl}/api/analytics/distributions${qs}`, { headers }),
      ]);

      if (summaryRes.status === 403 || dailyRes.status === 403 || distRes.status === 403) {
        setAnalyticsForbidden(true);
        setAnalyticsError('Admin Privileges Required: System-wide analytics endpoints require the administrative role (role=admin). Your current account is restricted.');
        return;
      }

      if (summaryRes.status === 401 || dailyRes.status === 401 || distRes.status === 401) {
        handleLogout();
        setAnalyticsError('Session expired. Please log in again.');
        return;
      }

      if (!summaryRes.ok) {
        const errData = await summaryRes.json().catch(() => ({}));
        throw new Error(errData.message || `Failed to fetch summary (HTTP ${summaryRes.status})`);
      }

      const summaryData = await summaryRes.json();
      const dailyData = await dailyRes.json();
      const distData = await distRes.json();

      setAnalyticsSummary(summaryData.summary);
      setDailyActivity(dailyData.daily_activity || []);
      setAnalyticsDistributions(distData.distributions || { categories: [], tones: [], languages: [], error_codes: [] });
      setIsAnalyticsEmpty(summaryData.is_empty);
    } catch (err: unknown) {
      setAnalyticsError(err instanceof Error ? err.message : 'Failed to load analytics data.');
    } finally {
      setAnalyticsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'analytics') {
      loadAnalyticsData();
    }
  }, [activeTab, startDate, endDate, selectedCategory]);

  // Export CSV Handler
  const handleExportCsv = async () => {
    if (!authToken) {
      setShowAuthModal(true);
      return;
    }
    setExportingCsv(true);
    setExportMessage(null);

    const queryParams = new URLSearchParams();
    if (startDate) queryParams.append('start_date', startDate);
    if (endDate) queryParams.append('end_date', endDate);
    if (selectedCategory && selectedCategory !== 'All') queryParams.append('category', selectedCategory);
    const qs = queryParams.toString() ? `?${queryParams.toString()}` : '';

    try {
      const res = await fetch(`${apiBaseUrl}/api/analytics/export.csv${qs}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (res.status === 403) {
        setAnalyticsForbidden(true);
        throw new Error('CSV Export requires administrative permissions (role=admin).');
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || `Export failed (HTTP ${res.status})`);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `SmartMail_Analytics_Summary_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setExportMessage('CSV report downloaded successfully!');
      setTimeout(() => setExportMessage(null), 3500);
    } catch (err: unknown) {
      setExportMessage(err instanceof Error ? err.message : 'CSV export failed.');
    } finally {
      setExportingCsv(false);
    }
  };

  // Handle Login & Register submission
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);

    const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';

    try {
      const res = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPassword }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || data.error || 'Authentication failed');
      }

      if (authMode === 'login') {
        const token = data.access_token;
        setAuthToken(token);
        sessionStorage.setItem('smartmail_token', token);
        setCurrentUser(data.user);
        setShowAuthModal(false);
        setAuthPassword('');
      } else {
        setAuthMode('login');
        setAuthError('Registration successful! Please log in with your credentials.');
      }
    } catch (err: unknown) {
      setAuthError(err instanceof Error ? err.message : 'Authentication error');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setAuthToken(null);
    setCurrentUser(null);
    sessionStorage.removeItem('smartmail_token');
  };

  // Generate Email request
  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!authToken) {
      setShowAuthModal(true);
      return;
    }

    if (!purpose.trim() || purpose.trim().length < 5) {
      setGenerationError("Please enter a clear email purpose (at least 5 characters).");
      return;
    }

    setGenerating(true);
    setGenerationError(null);

    const payload = {
      purpose: purpose.trim(),
      category,
      tone,
      length: lengthPref,
      language,
      recipient: recipient.trim(),
      key_points: keyPoints.trim(),
      additional_context: additionalContext.trim(),
    };

    try {
      const res = await fetch(`${apiBaseUrl}/api/email/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        if (res.status === 401) {
          handleLogout();
          throw new Error("Your session has expired. Please log in again.");
        }
        if (res.status === 503) {
          throw new Error("AI Service Notice: OPENAI_API_KEY is not configured in backend environment. Please set OPENAI_API_KEY in backend/.env.");
        }
        throw new Error(data.message || data.error || `Generation failed (HTTP ${res.status})`);
      }

      const draft: EmailDraft = data.draft;
      setCurrentDraft(draft);
      setEditableSubject(draft.subject);
      setEditableBody(draft.body);
    } catch (err: unknown) {
      setGenerationError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  // Clipboard actions
  const handleCopy = async (text: string, type: 'subject' | 'body' | 'full') => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'subject') {
        setCopiedSubject(true);
        setTimeout(() => setCopiedSubject(false), 2000);
      } else if (type === 'body') {
        setCopiedBody(true);
        setTimeout(() => setCopiedBody(false), 2000);
      } else {
        setCopiedFull(true);
        setTimeout(() => setCopiedFull(false), 2000);
      }
    } catch {
      // Fallback
    }
  };

  // Download draft as .txt file
  const handleDownloadTxt = () => {
    if (!editableSubject && !editableBody) return;
    const content = `Subject: ${editableSubject}\n\n${editableBody}\n\n---\nGenerated with SmartMail AI (${currentDraft?.category || category} | ${currentDraft?.tone || tone})`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `SmartMail_${category.replace(/\s+/g, '_')}_Draft.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Navigation Header */}
      <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
              <Mail className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight text-white">SmartMail AI</span>
              <span className="ml-2 text-xs font-mono uppercase bg-indigo-950 text-indigo-300 border border-indigo-800 px-2 py-0.5 rounded-full">
                Phase 3 Analytics
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Live Health Badge */}
            <div className="hidden sm:flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-lg border bg-slate-900 border-slate-800">
              {healthLoading ? (
                <RefreshCw className="w-3 h-3 text-slate-400 animate-spin" />
              ) : health ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">API: {health.status}</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-amber-400">API: Offline</span>
                </>
              )}
            </div>

            {/* Navigation Switch */}
            <div className="flex rounded-lg bg-slate-900 p-0.5 border border-slate-800 text-xs">
              <button
                onClick={() => setActiveTab('generator')}
                className={`px-3 py-1 rounded-md font-medium transition ${
                  activeTab === 'generator'
                    ? 'bg-sky-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Generator
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`px-3 py-1 rounded-md font-medium transition flex items-center gap-1.5 ${
                  activeTab === 'analytics'
                    ? 'bg-indigo-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <BarChart3 className="w-3 h-3" />
                <span>Analytics</span>
              </button>
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-3 py-1 rounded-md font-medium transition ${
                  activeTab === 'overview'
                    ? 'bg-sky-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Overview
              </button>
            </div>

            {/* Authentication state */}
            {currentUser ? (
              <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
                <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
                  <UserIcon className="w-3.5 h-3.5 text-sky-400" />
                  <span className="max-w-[120px] truncate">{currentUser.email}</span>
                  <span className="text-[10px] font-mono px-1 py-0.2 bg-slate-800 rounded text-slate-400 uppercase">
                    {currentUser.role}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  title="Log Out"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
                className="inline-flex items-center space-x-1.5 text-xs bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white px-3 py-1.5 rounded-lg font-medium shadow transition"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Log In</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* TAB 1: GENERATOR */}
        {activeTab === 'generator' && (
          <div className="space-y-8">
            {/* Page Header */}
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                AI Email Generator
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Generate high-impact academic outreach, formal inquiries, and professional correspondence using structured prompt engineering.
              </p>
            </div>

            {/* Unauthenticated Alert Prompt */}
            {!currentUser && (
              <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-800/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex items-center space-x-3">
                  <ShieldCheck className="w-5 h-5 text-sky-400 shrink-0" />
                  <div className="text-xs text-sky-200">
                    <span className="font-semibold text-white">Authentication Required: </span>
                    Per Security Engineering rules, email generation requires an authenticated session. Register or log in to generate drafts.
                  </div>
                </div>
                <button
                  onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
                  className="shrink-0 px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold shadow transition"
                >
                  Log In / Register
                </button>
              </div>
            )}

            {/* Main Generator Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Left Column: Input Form (5 cols) */}
              <div className="lg:col-span-5 bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-5">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-sky-400" />
                    <span>Generation Parameters</span>
                  </h2>
                  <span className="text-xs text-slate-400 font-mono">OpenAI gpt-4o-mini</span>
                </div>

                <form onSubmit={handleGenerate} className="space-y-4">
                  {/* Category */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Email Category *
                    </label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-2.5 focus:border-sky-500 focus:outline-none transition"
                    >
                      {options.categories.map((cat) => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>

                  {/* Purpose Input */}
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <label className="block text-xs font-semibold text-slate-300">
                        Primary Purpose *
                      </label>
                      <span className="text-[10px] text-slate-500 font-mono">
                        {purpose.length}/1000
                      </span>
                    </div>
                    <textarea
                      rows={4}
                      value={purpose}
                      onChange={(e) => setPurpose(e.target.value)}
                      placeholder="e.g., Request a meeting with Professor Smith to discuss research opportunities in artificial intelligence for my graduate thesis..."
                      className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-3 focus:border-sky-500 focus:outline-none transition placeholder-slate-600 leading-relaxed"
                    />
                  </div>

                  {/* Tone & Length Grid */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Tone *
                      </label>
                      <select
                        value={tone}
                        onChange={(e) => setTone(e.target.value)}
                        className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-2.5 focus:border-sky-500 focus:outline-none transition"
                      >
                        {options.tones.map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Target Length *
                      </label>
                      <select
                        value={lengthPref}
                        onChange={(e) => setLengthPref(e.target.value)}
                        className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-2.5 focus:border-sky-500 focus:outline-none transition"
                      >
                        {options.lengths.map((len) => (
                          <option key={len} value={len}>{len}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Language */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Output Language
                    </label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-2.5 focus:border-sky-500 focus:outline-none transition"
                    >
                      {options.languages.map((lang) => (
                        <option key={lang} value={lang}>{lang}</option>
                      ))}
                    </select>
                  </div>

                  {/* Toggle Advanced Inputs */}
                  <div className="pt-1">
                    <button
                      type="button"
                      onClick={() => setShowAdvanced(!showAdvanced)}
                      className="text-xs text-sky-400 hover:text-sky-300 font-medium inline-flex items-center gap-1"
                    >
                      <span>{showAdvanced ? '− Hide Context Fields' : '+ Add Recipient & Key Points'}</span>
                    </button>
                  </div>

                  {/* Advanced Inputs */}
                  {showAdvanced && (
                    <div className="space-y-3 pt-2 border-t border-slate-800/80">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">
                          Recipient Context (Optional)
                        </label>
                        <input
                          type="text"
                          value={recipient}
                          onChange={(e) => setRecipient(e.target.value)}
                          placeholder="e.g., Dr. Jane Smith, Department Chair"
                          className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-2.5 focus:border-sky-500 focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">
                          Key Points to Include (Optional)
                        </label>
                        <input
                          type="text"
                          value={keyPoints}
                          onChange={(e) => setKeyPoints(e.target.value)}
                          placeholder="e.g., Mention prior paper on Transformers; suggest 15-min Zoom"
                          className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-2.5 focus:border-sky-500 focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">
                          Additional Background / Constraints (Optional)
                        </label>
                        <textarea
                          rows={2}
                          value={additionalContext}
                          onChange={(e) => setAdditionalContext(e.target.value)}
                          placeholder="e.g., Available on Tuesday or Thursday afternoons"
                          className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-100 p-2.5 focus:border-sky-500 focus:outline-none"
                        />
                      </div>
                    </div>
                  )}

                  {/* Error Message */}
                  {generationError && (
                    <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl text-xs text-rose-300 flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                      <span>{generationError}</span>
                    </div>
                  )}

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={generating}
                    className="w-full py-3 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-lg shadow-sky-500/10 flex items-center justify-center gap-2 transition"
                  >
                    {generating ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin text-white" />
                        <span>Generating Draft with OpenAI...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 text-white" />
                        <span>Generate Email Draft</span>
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Right Column: Output & Live Editor (7 cols) */}
              <div className="lg:col-span-7 bg-slate-900/70 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                    <div className="flex items-center space-x-2">
                      <h2 className="text-base font-bold text-white">Generated Email Draft</h2>
                      {currentDraft && (
                        <span className="text-[11px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded-full">
                          Ready & Editable
                        </span>
                      )}
                    </div>

                    {currentDraft && (
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleCopy(editableSubject ? `Subject: ${editableSubject}\n\n${editableBody}` : editableBody, 'full')}
                          className="px-2.5 py-1 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition flex items-center gap-1.5"
                          title="Copy Full Draft"
                        >
                          {copiedFull ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                          <span>{copiedFull ? 'Copied!' : 'Copy All'}</span>
                        </button>
                        <button
                          onClick={handleDownloadTxt}
                          className="px-2.5 py-1 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition flex items-center gap-1.5"
                          title="Download as .txt"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>.TXT</span>
                        </button>
                      </div>
                    )}
                  </div>

                  {generating ? (
                    <div className="h-96 flex flex-col items-center justify-center text-center space-y-3">
                      <div className="w-12 h-12 rounded-2xl bg-sky-950 border border-sky-800 flex items-center justify-center text-sky-400 animate-pulse">
                        <Sparkles className="w-6 h-6 animate-spin" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-white">Synthesizing Professional Draft</p>
                        <p className="text-xs text-slate-400 mt-1 max-w-sm">
                          Structuring tone, formatting placeholders, and applying defensive prompt isolation...
                        </p>
                      </div>
                    </div>
                  ) : currentDraft ? (
                    <div className="space-y-4">
                      {/* Subject Line Editor */}
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <label className="block text-xs font-semibold text-slate-300">Subject Line</label>
                          <button
                            onClick={() => handleCopy(editableSubject, 'subject')}
                            className="text-[11px] text-sky-400 hover:text-sky-300 flex items-center gap-1"
                          >
                            {copiedSubject ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                            <span>{copiedSubject ? 'Copied' : 'Copy Subject'}</span>
                          </button>
                        </div>
                        <input
                          type="text"
                          value={editableSubject}
                          onChange={(e) => setEditableSubject(e.target.value)}
                          className="w-full text-xs font-semibold rounded-xl bg-slate-950 border border-slate-800 text-white p-3 focus:border-sky-500 focus:outline-none"
                        />
                      </div>

                      {/* Body Editor */}
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <label className="block text-xs font-semibold text-slate-300">Email Body</label>
                          <button
                            onClick={() => handleCopy(editableBody, 'body')}
                            className="text-[11px] text-sky-400 hover:text-sky-300 flex items-center gap-1"
                          >
                            {copiedBody ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                            <span>{copiedBody ? 'Copied' : 'Copy Body'}</span>
                          </button>
                        </div>
                        <textarea
                          rows={14}
                          value={editableBody}
                          onChange={(e) => setEditableBody(e.target.value)}
                          className="w-full text-xs font-mono rounded-xl bg-slate-950 border border-slate-800 text-slate-200 p-3.5 focus:border-sky-500 focus:outline-none leading-relaxed resize-y"
                        />
                      </div>

                      {/* Provider Token & Metadata Badge */}
                      {currentDraft.usage && (
                        <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2">
                          <div className="flex items-center gap-3">
                            <span>Tokens: <strong className="text-slate-200">{currentDraft.usage.total_tokens}</strong> ({currentDraft.usage.prompt_tokens} in / {currentDraft.usage.completion_tokens} out)</span>
                            <span>Model: <strong className="text-slate-200">{currentDraft.model}</strong></span>
                          </div>
                          <span className="text-emerald-400">Telemetry event recorded</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="h-96 flex flex-col items-center justify-center text-center p-6 border-2 border-dashed border-slate-800 rounded-2xl">
                      <div className="w-12 h-12 rounded-xl bg-slate-800/60 flex items-center justify-center text-slate-500 mb-3">
                        <Send className="w-6 h-6" />
                      </div>
                      <p className="text-sm font-semibold text-slate-300">No Draft Generated Yet</p>
                      <p className="text-xs text-slate-500 mt-1 max-w-sm">
                        Fill in your email purpose and generation parameters on the left, then click "Generate Email Draft" to create your draft.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ANALYTICS DASHBOARD (PHASE 3) */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Header with Title and Actions */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
              <div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
                  <BarChart3 className="w-7 h-7 text-indigo-400" />
                  <span>Analytics & Telemetry Dashboard</span>
                </h1>
                <p className="text-sm text-slate-400 mt-1">
                  Database-backed aggregate metrics, time-series generation volume, and repeatable Pandas ETL telemetry.
                </p>
              </div>

              {/* Actions: Refresh & CSV Export */}
              <div className="flex items-center space-x-2.5">
                <button
                  onClick={loadAnalyticsData}
                  disabled={analyticsLoading}
                  className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition border border-slate-700"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${analyticsLoading ? 'animate-spin' : ''}`} />
                  <span>Refresh</span>
                </button>

                <button
                  onClick={handleExportCsv}
                  disabled={exportingCsv || analyticsForbidden}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow-lg shadow-indigo-600/20"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5" />
                  <span>{exportingCsv ? 'Exporting...' : 'Export Aggregate CSV'}</span>
                </button>
              </div>
            </div>

            {/* Export Notification */}
            {exportMessage && (
              <div className="p-3 bg-emerald-950/60 border border-emerald-800 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{exportMessage}</span>
              </div>
            )}

            {/* Filter Controls Bar */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center space-x-2 text-xs text-slate-400">
                  <Calendar className="w-4 h-4 text-slate-500" />
                  <span>Date Range:</span>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2.5 py-1.5 focus:border-indigo-500 focus:outline-none"
                  />
                  <span className="text-xs text-slate-500">to</span>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2.5 py-1.5 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
                  <Filter className="w-3.5 h-3.5 text-slate-500" />
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2.5 py-1.5 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="All">All Categories</option>
                    {options.categories.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="text-xs text-slate-500 font-mono">
                Pipeline: Pandas 2.2.2 ETL · UTC Aggregation
              </div>
            </div>

            {/* Role / RBAC Warnings */}
            {analyticsForbidden && (
              <div className="p-5 rounded-2xl bg-amber-950/30 border border-amber-800/60 space-y-3">
                <div className="flex items-center space-x-3 text-amber-300 font-bold text-sm">
                  <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
                  <span>Administrative Role Required (RBAC DAT-05)</span>
                </div>
                <p className="text-xs text-amber-200/90 leading-relaxed">
                  System-wide analytics and CSV exports are strictly protected by Role-Based Access Control (<code className="bg-amber-950 px-1 py-0.5 rounded text-amber-300">@roles_required('admin')</code>). Your current account role is <strong className="text-white">'{currentUser?.role || 'user'}'</strong>.
                </p>
                <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl text-xs text-slate-400">
                  <strong className="text-slate-200">How to access Administrator Analytics:</strong>
                  <ul className="list-disc list-inside mt-1 space-y-1 text-[11px]">
                    <li>Sign in with an administrative test account (e.g. <code className="text-sky-300">analytics_admin@wipro.com</code>).</li>
                    <li>Or verify with the automated test suite in <code className="text-sky-300">backend/tests/test_analytics.py</code> where admin RBAC is verified.</li>
                  </ul>
                </div>
              </div>
            )}

            {/* Error Message (if not 403) */}
            {analyticsError && !analyticsForbidden && (
              <div className="p-4 bg-rose-950/40 border border-rose-800/60 rounded-xl text-xs text-rose-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span>{analyticsError}</span>
              </div>
            )}

            {/* Loading Indicator */}
            {analyticsLoading && (
              <div className="py-20 flex flex-col items-center justify-center text-center space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-indigo-950 border border-indigo-800 flex items-center justify-center text-indigo-400 animate-pulse">
                  <RefreshCw className="w-6 h-6 animate-spin" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Running Pandas ETL Pipeline</p>
                  <p className="text-xs text-slate-400 mt-1">Extracting telemetry events and aggregating metrics...</p>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!analyticsLoading && !analyticsForbidden && isAnalyticsEmpty && (
              <div className="py-16 text-center border-2 border-dashed border-slate-800 rounded-2xl p-8 space-y-3">
                <div className="w-12 h-12 rounded-xl bg-slate-900 mx-auto flex items-center justify-center text-slate-500">
                  <BarChart3 className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-200">No Analytics Telemetry Recorded</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                  No generation events found matching the selected timeframe. Switch to the Email Generator, produce drafts with an authenticated account, and the real database events will automatically reflect here.
                </p>
                <button
                  onClick={() => setActiveTab('generator')}
                  className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-xl shadow transition"
                >
                  Go to Email Generator
                </button>
              </div>
            )}

            {/* Real Analytics Data Display */}
            {!analyticsLoading && !analyticsForbidden && !isAnalyticsEmpty && analyticsSummary && (
              <div className="space-y-6">
                {/* 4 KPI Summary Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Card 1: Total Recorded */}
                  <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                        <span>Total Generations</span>
                        <Mail className="w-4 h-4 text-sky-400" />
                      </div>
                      <div className="text-3xl font-extrabold text-white tracking-tight">
                        {analyticsSummary.total_events}
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 flex justify-between">
                      <span className="text-emerald-400 font-medium">{analyticsSummary.successful_events} Successful</span>
                      <span className="text-rose-400 font-medium">{analyticsSummary.failed_events} Failed</span>
                    </div>
                  </div>

                  {/* Card 2: Success Rate */}
                  <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                        <span>Success Rate</span>
                        <TrendingUp className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div className="text-3xl font-extrabold text-white tracking-tight">
                        {analyticsSummary.success_rate !== null ? `${analyticsSummary.success_rate}%` : 'N/A'}
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-800/80">
                      <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div 
                          className="bg-emerald-500 h-1.5 rounded-full" 
                          style={{ width: `${analyticsSummary.success_rate || 0}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Card 3: Avg Duration */}
                  <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                        <span>Average Latency</span>
                        <Clock className="w-4 h-4 text-indigo-400" />
                      </div>
                      <div className="text-3xl font-extrabold text-white tracking-tight">
                        {analyticsSummary.avg_duration_ms !== null ? `${analyticsSummary.avg_duration_ms} ms` : 'N/A'}
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                      Median: {analyticsSummary.median_duration_ms !== null ? `${analyticsSummary.median_duration_ms} ms` : 'N/A'}
                    </div>
                  </div>

                  {/* Card 4: Tokens */}
                  <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
                        <span>Provider AI Tokens</span>
                        <Coins className="w-4 h-4 text-amber-400" />
                      </div>
                      <div className="text-3xl font-extrabold text-white tracking-tight">
                        {analyticsSummary.total_tokens !== null ? analyticsSummary.total_tokens.toLocaleString() : 'N/A'}
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 flex justify-between">
                      <span>Avg: {analyticsSummary.avg_tokens || 'N/A'}</span>
                      <span>Prompt: {analyticsSummary.prompt_tokens_total || 0}</span>
                    </div>
                  </div>
                </div>

                {/* Daily Activity Over Time Table */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <h2 className="text-base font-bold text-white flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-indigo-400" />
                      <span>Daily Activity Over Time</span>
                    </h2>
                    <span className="text-xs text-slate-400 font-mono">
                      {dailyActivity.length} Days Recorded
                    </span>
                  </div>

                  {dailyActivity.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                            <th className="py-2.5 px-3">Date</th>
                            <th className="py-2.5 px-3">Total Requests</th>
                            <th className="py-2.5 px-3">Success / Fail</th>
                            <th className="py-2.5 px-3">Success Rate</th>
                            <th className="py-2.5 px-3">Avg Latency</th>
                            <th className="py-2.5 px-3">Total Tokens</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-mono">
                          {dailyActivity.map((day) => (
                            <tr key={day.date} className="hover:bg-slate-800/30 transition">
                              <td className="py-2.5 px-3 text-slate-200 font-semibold">{day.date}</td>
                              <td className="py-2.5 px-3 text-white">{day.total}</td>
                              <td className="py-2.5 px-3">
                                <span className="text-emerald-400">{day.successful}</span> / <span className="text-rose-400">{day.failed}</span>
                              </td>
                              <td className="py-2.5 px-3">
                                <span className={day.success_rate && day.success_rate >= 90 ? 'text-emerald-400' : 'text-amber-400'}>
                                  {day.success_rate !== null ? `${day.success_rate}%` : 'N/A'}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-slate-300">
                                {day.avg_duration_ms !== null ? `${day.avg_duration_ms} ms` : 'N/A'}
                              </td>
                              <td className="py-2.5 px-3 text-slate-300">
                                {day.total_tokens !== null ? day.total_tokens.toLocaleString() : 'N/A'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 py-4 text-center">No daily activity recorded for this filter.</p>
                  )}
                </div>

                {/* Categorical Distributions (Grid 2 cols) */}
                {analyticsDistributions && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Categories Breakdown */}
                    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                        <h2 className="text-base font-bold text-white flex items-center gap-2">
                          <PieChart className="w-4 h-4 text-sky-400" />
                          <span>Category Distribution</span>
                        </h2>
                        <span className="text-xs text-slate-400">
                          {analyticsDistributions.categories.length} Unique
                        </span>
                      </div>

                      <div className="space-y-3">
                        {analyticsDistributions.categories.map((item) => (
                          <div key={item.label} className="space-y-1">
                            <div className="flex justify-between text-xs">
                              <span className="text-slate-300 font-medium">{item.label}</span>
                              <span className="text-slate-400 font-mono">{item.count} ({item.percentage}%)</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                              <div
                                className="bg-sky-500 h-1.5 rounded-full"
                                style={{ width: `${item.percentage}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Tone & Language Breakdown */}
                    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-5">
                      {/* Tone */}
                      <div>
                        <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
                          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                            Tone Distribution
                          </h3>
                        </div>
                        <div className="space-y-2.5">
                          {analyticsDistributions.tones.map((item) => (
                            <div key={item.label} className="space-y-1">
                              <div className="flex justify-between text-xs">
                                <span className="text-slate-300">{item.label}</span>
                                <span className="text-slate-400 font-mono">{item.count} ({item.percentage}%)</span>
                              </div>
                              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className="bg-indigo-500 h-1.5 rounded-full"
                                  style={{ width: `${item.percentage}%` }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Language */}
                      <div className="pt-2">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
                          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                            Language Distribution
                          </h3>
                        </div>
                        <div className="space-y-2.5">
                          {analyticsDistributions.languages.map((item) => (
                            <div key={item.label} className="space-y-1">
                              <div className="flex justify-between text-xs">
                                <span className="text-slate-300">{item.label}</span>
                                <span className="text-slate-400 font-mono">{item.count} ({item.percentage}%)</span>
                              </div>
                              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className="bg-emerald-500 h-1.5 rounded-full"
                                  style={{ width: `${item.percentage}%` }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Error Diagnostics (if any failures recorded) */}
                {analyticsDistributions && analyticsDistributions.error_codes.length > 0 && (
                  <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                      <h2 className="text-base font-bold text-white flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-rose-400" />
                        <span>Failure Code Diagnostics</span>
                      </h2>
                      <span className="text-xs text-rose-400 font-medium">Sanitized Exception Classification</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {analyticsDistributions.error_codes.map((err) => (
                        <div key={err.label} className="p-3 bg-rose-950/20 border border-rose-900/40 rounded-xl">
                          <div className="text-xs font-mono font-semibold text-rose-300 truncate" title={err.label}>
                            {err.label}
                          </div>
                          <div className="text-lg font-extrabold text-white mt-1">
                            {err.count} <span className="text-xs font-normal text-slate-400">({err.percentage}%)</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <section className="text-center py-6">
              <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                Enterprise Email Generation Platform
              </h1>
              <p className="text-sm text-slate-400 mt-2 max-w-2xl mx-auto leading-relaxed">
                SmartMail AI demonstrates AI Engineering, Security Engineering, Data Engineering, and Cloud Engineering in a unified, audit-compliant architecture.
              </p>
            </section>

            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-sky-950 flex items-center justify-center text-sky-400 mb-3 border border-sky-800">
                    <Brain className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">AI Engineering</h3>
                  <p className="text-xs text-slate-400">
                    OpenAI Python SDK, prompt injection defense, structured JSON schema outputs, and tone/length controls.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800 text-xs font-semibold text-emerald-400">
                  Status: Phase 2 Verified
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-indigo-950 flex items-center justify-center text-indigo-400 mb-3 border border-indigo-800">
                    <Database className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">Data Engineering</h3>
                  <p className="text-xs text-slate-400">
                    Privacy-conscious telemetry logging, Pandas 2.2.2 ETL aggregation, and formula-injection-safe CSV exports.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800 text-xs font-semibold text-emerald-400">
                  Status: Phase 3 Verified
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-slate-950 flex items-center justify-center text-slate-400 mb-3 border border-slate-800">
                    <Cloud className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">Cloud Engineering</h3>
                  <p className="text-xs text-slate-400">
                    Docker containerization, Amazon RDS PostgreSQL migration, S3 storage, and CI/CD.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800 text-xs font-semibold text-slate-500">
                  Status: Planned (Phase 4)
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-rose-950 flex items-center justify-center text-rose-400 mb-3 border border-rose-800">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">Security Engineering</h3>
                  <p className="text-xs text-slate-400">
                    JWT authentication, Werkzeug password hashing, rate limiting, and automated security tests.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800 text-xs font-semibold text-emerald-400">
                  Status: Phase 1 Verified
                </div>
              </div>
            </section>
          </div>
        )}
      </main>

      {/* Authentication Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-sm w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-base text-white">
                {authMode === 'login' ? 'Sign In to SmartMail AI' : 'Create New Account'}
              </h3>
              <button
                onClick={() => setShowAuthModal(false)}
                className="text-slate-400 hover:text-white text-xs"
              >
                &times; Close
              </button>
            </div>

            <form onSubmit={handleAuthSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  placeholder="name@university.edu"
                  className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-white p-2.5 focus:border-sky-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  placeholder="Min 8 chars, 1 letter, 1 number"
                  className="w-full text-xs rounded-xl bg-slate-950 border border-slate-800 text-white p-2.5 focus:border-sky-500 focus:outline-none"
                />
              </div>

              {authError && (
                <div className="p-2.5 bg-rose-950/40 border border-rose-800/60 rounded-lg text-xs text-rose-300">
                  {authError}
                </div>
              )}

              <button
                type="submit"
                disabled={authLoading}
                className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs rounded-xl shadow transition"
              >
                {authLoading ? 'Processing...' : authMode === 'login' ? 'Sign In' : 'Register Account'}
              </button>

              <div className="text-center pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode(authMode === 'login' ? 'register' : 'login');
                    setAuthError(null);
                  }}
                  className="text-xs text-sky-400 hover:text-sky-300 underline"
                >
                  {authMode === 'login' ? "Don't have an account? Register" : 'Already have an account? Sign In'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <div>SmartMail AI &copy; 2026. Antigravity IDE Workspace.</div>
          <div className="flex items-center space-x-4">
            <span>AI Module (P2)</span>
            <span>Security Module (P1)</span>
            <span>Data Module (P3)</span>
            <span>Cloud Module (P4)</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
