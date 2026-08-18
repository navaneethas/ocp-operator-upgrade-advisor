import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, AlertCircle } from 'lucide-react';
import { analyzeCluster } from '../services/api';

const OCP_VERSIONS = ['4.12', '4.13', '4.14', '4.15', '4.16', '4.17'];

interface FileInputProps {
  label: string;
  description: string;
  onChange: (data: any) => void;
  error?: string;
}

const FileInput = ({ label, description, onChange, error }: FileInputProps) => {
  const [fileName, setFileName] = useState<string>('');

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        onChange(json);
      } catch (err) {
        alert(`Error parsing JSON file: ${err}`);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <p className="text-xs text-gray-500 mb-2">{description}</p>
      <div className="flex items-center gap-2">
        <label className="flex-1 flex items-center justify-center px-4 py-6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-red-400 bg-white">
          <Upload className="w-5 h-5 text-gray-400 mr-2" />
          <span className="text-sm text-gray-600">
            {fileName || 'Choose JSON file'}
          </span>
          <input type="file" accept=".json" className="hidden" onChange={handleFileChange} />
        </label>
      </div>
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  );
};

const UploadPage = () => {
  const navigate = useNavigate();
  const [targetVersion, setTargetVersion] = useState<string>('4.16');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const [files, setFiles] = useState({
    clusterversion_json: null,
    subscriptions_json: null,
    csv_json: null,
    catalogsource_json: null,
    packagemanifest_json: null,
  });

  const handleAnalyze = async () => {
    const missing = Object.entries(files).filter(([_, value]) => !value);

    if (missing.length > 0) {
      setError('Please upload all required JSON files');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await analyzeCluster({
        ...files,
        target_ocp_version: targetVersion,
      } as any);

      navigate(`/results/${result.analysis_id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold mb-6">Upload Cluster Data</h2>

        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Instructions:</strong> Run the following commands on your OpenShift cluster and
            upload the resulting JSON files:
          </p>
          <ul className="mt-2 text-xs text-blue-700 space-y-1 font-mono">
            <li>oc get clusterversion version -o json &gt; clusterversion.json</li>
            <li>oc get sub -A -o json &gt; subscriptions.json</li>
            <li>oc get csv -A -o json &gt; csv.json</li>
            <li>oc get catalogsource -A -o json &gt; catalogsource.json</li>
            <li>oc get packagemanifest -o json &gt; packagemanifest.json</li>
          </ul>
        </div>

        <FileInput
          label="Cluster Version"
          description="oc get clusterversion version -o json"
          onChange={(data) => setFiles({ ...files, clusterversion_json: data })}
        />

        <FileInput
          label="Subscriptions"
          description="oc get sub -A -o json"
          onChange={(data) => setFiles({ ...files, subscriptions_json: data })}
        />

        <FileInput
          label="ClusterServiceVersions (CSV)"
          description="oc get csv -A -o json"
          onChange={(data) => setFiles({ ...files, csv_json: data })}
        />

        <FileInput
          label="Catalog Sources"
          description="oc get catalogsource -A -o json"
          onChange={(data) => setFiles({ ...files, catalogsource_json: data })}
        />

        <FileInput
          label="Package Manifests"
          description="oc get packagemanifest -o json"
          onChange={(data) => setFiles({ ...files, packagemanifest_json: data })}
        />

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target OpenShift Version
          </label>
          <select
            value={targetVersion}
            onChange={(e) => setTargetVersion(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          >
            {OCP_VERSIONS.map((version) => (
              <option key={version} value={version}>
                {version}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg transition-colors"
        >
          {loading ? 'Analyzing...' : 'Analyze Compatibility'}
        </button>
      </div>
    </div>
  );
};

export default UploadPage;
