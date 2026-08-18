import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  CheckCircle,
  AlertTriangle,
  AlertCircle,
  XCircle,
  Download,
  ArrowLeft,
} from 'lucide-react';
import { getAnalysis, downloadHtmlReport, downloadJsonReport } from '../services/api';
import { AnalysisResponse, CompatibilityStatus, RiskLevel } from '../types';

const statusConfig = {
  compatible: {
    icon: CheckCircle,
    color: 'text-green-600',
    bg: 'bg-green-50',
    label: 'Compatible',
  },
  upgrade_required: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bg: 'bg-yellow-50',
    label: 'Upgrade Required',
  },
  manual_intervention: {
    icon: AlertCircle,
    color: 'text-orange-600',
    bg: 'bg-orange-50',
    label: 'Manual Intervention',
  },
  unsupported: {
    icon: XCircle,
    color: 'text-red-600',
    bg: 'bg-red-50',
    label: 'Unsupported',
  },
};

const riskConfig: Record<RiskLevel, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

const ResultsPage = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const loadAnalysis = async () => {
      if (!analysisId) return;

      try {
        const data = await getAnalysis(analysisId);
        setAnalysis(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load analysis');
      } finally {
        setLoading(false);
      }
    };

    loadAnalysis();
  }, [analysisId]);

  const handleDownloadHtml = async () => {
    if (!analysisId) return;
    try {
      const blob = await downloadHtmlReport(analysisId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `openshift-upgrade-report-${analysisId}.html`;
      a.click();
    } catch (err) {
      alert('Failed to download HTML report');
    }
  };

  const handleDownloadJson = async () => {
    if (!analysisId) return;
    try {
      const blob = await downloadJsonReport(analysisId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `openshift-upgrade-report-${analysisId}.json`;
      a.click();
    } catch (err) {
      alert('Failed to download JSON report');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error || 'Analysis not found'}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 text-red-600 hover:text-red-700 font-medium"
          >
            ← Back to Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-800"
      >
        <ArrowLeft className="w-4 h-4" />
        New Analysis
      </button>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">Cluster Analysis</h2>
            <p className="text-gray-600">
              {analysis.cluster_info.current_version} → {analysis.cluster_info.target_version}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDownloadHtml}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm"
            >
              <Download className="w-4 h-4" />
              HTML
            </button>
            <button
              onClick={handleDownloadJson}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm"
            >
              <Download className="w-4 h-4" />
              JSON
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-800">
              {analysis.cluster_info.total_operators}
            </div>
            <div className="text-sm text-gray-600">Total Operators</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {analysis.cluster_info.compatible_count}
            </div>
            <div className="text-sm text-gray-600">Compatible</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {analysis.cluster_info.upgrade_required_count}
            </div>
            <div className="text-sm text-gray-600">Upgrade Required</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {analysis.cluster_info.manual_count}
            </div>
            <div className="text-sm text-gray-600">Manual</div>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {analysis.cluster_info.unsupported_count}
            </div>
            <div className="text-sm text-gray-600">Unsupported</div>
          </div>
        </div>

        <div className="mt-6">
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${riskConfig[analysis.risk_score]}`}>
            Risk: {analysis.risk_score.toUpperCase()}
          </span>
        </div>
      </div>

      {analysis.ai_summary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 className="font-bold text-blue-900 mb-2">AI Summary</h3>
          <p className="text-blue-800">{analysis.ai_summary}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-4">Operator Compatibility</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-700">Operator</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Current</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Target</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Explanation</th>
              </tr>
            </thead>
            <tbody>
              {analysis.compatibility_results.map((result, idx) => {
                const config = statusConfig[result.status as CompatibilityStatus];
                const Icon = config.icon;

                return (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{result.operator_name}</td>
                    <td className="py-3 px-4 text-gray-600">{result.current_version}</td>
                    <td className="py-3 px-4 text-gray-600">
                      {result.target_version || 'N/A'}
                    </td>
                    <td className="py-3 px-4">
                      <div className={`flex items-center gap-2 ${config.color}`}>
                        <Icon className="w-4 h-4" />
                        <span className="text-sm">{config.label}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {result.explanation || 'No explanation available'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {Object.keys(analysis.upgrade_paths).length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-xl font-bold mb-4">Upgrade Paths</h3>
          {Object.entries(analysis.upgrade_paths).map(([name, path]) => (
            <div key={name} className="mb-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-bold text-gray-800">{name}</h4>
              <p className="text-sm text-gray-600 mt-1">
                Path: {path.path.join(' → ')}
              </p>
              <p className="text-sm text-gray-600">Steps: {path.steps}</p>
              <p className="text-sm text-gray-600">{path.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
