import { useState } from 'react'
import axios from 'axios'

// Configure Axios base URL - assuming backend on port 8000
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

function App() {
  const [activeTab, setActiveTab] = useState('call');

  return (
    <div className="app">
      <header className="header">
        <div className="container flex justify-between items-center">
          <div className="logo">
            <img src="/PCG_Toolkit_Logo.png" alt="PCG Toolkit Logo" style={{ height: '40px', objectFit: 'contain' }} />
            <span>Toolkit</span>
          </div>
          <nav className="flex gap-md">
            <TabButton active={activeTab === 'call'} onClick={() => setActiveTab('call')}>Log Call</TabButton>
            <TabButton active={activeTab === 'email'} onClick={() => setActiveTab('email')}>Log Email</TabButton>
            <TabButton active={activeTab === 'task'} onClick={() => setActiveTab('task')}>Log Task</TabButton>
            <TabButton active={activeTab === 'next_action'} onClick={() => setActiveTab('next_action')}>Next Actions</TabButton>
          </nav>
        </div>
      </header>

      <main className="container">
        {activeTab === 'call' && <CallLogger type="call" />}
        {activeTab === 'email' && <EmailLogger type="email" />}
        {activeTab === 'task' && <TaskLogger type="task" />}
        {activeTab === 'next_action' && <NextActionLogger type="next_action" />}
      </main>
    </div>
  )
}

function TabButton({ active, onClick, children }) {
  return (
    <button
      className={`btn ${active ? 'btn-primary' : ''}`}
      onClick={onClick}
      style={!active ? { background: 'transparent', color: 'var(--color-text)' } : {}}
    >
      {children}
    </button>
  )
}

// Reusable component for file upload and transcription
function TranscriptionControls({ onTranscribeComplete, isTranscribing, setIsTranscribing }) {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleTranscribe = async () => {
    if (!file) return;
    setIsTranscribing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onTranscribeComplete(response.data.transcription);
    } catch (error) {
      console.error("Transcription error", error);
      alert("Error transcribing audio");
    } finally {
      setIsTranscribing(false);
    }
  };

  return (
    <div className="input-group">
      <label className="label">Upload Recording (optional)</label>
      <div className="flex gap-md">
        <input
          type="file"
          accept="audio/*,.mp4"
          onChange={handleFileChange}
          className="input"
          style={{ lineHeight: '1.2' }}
        />
        <button
          className="btn btn-primary"
          onClick={handleTranscribe}
          disabled={!file || isTranscribing}
        >
          {isTranscribing ? 'Transcribing...' : 'Transcribe'}
        </button>
      </div>
    </div>
  );
}

function CallLogger() {
  const [transcript, setTranscript] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!transcript) return;
    setIsProcessing(true);
    setResult(null);
    try {
      const response = await api.post('/log_call', { user_input: transcript });
      setResult(response.data);
    } catch (error) {
      console.error("Processing error", error);
      let msg = "Error processing call log";
      if (error.response) {
        msg += ` (Status ${error.response.status}): ${JSON.stringify(error.response.data)}`;
      } else {
        msg += `: ${error.message}`;
      }
      alert(msg);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Log Phone Call</h2>
        <p className="text-muted mb-6">Upload a call recording or paste a transcript to generate CRM suggestions.</p>

        <TranscriptionControls
          onTranscribeComplete={(text) => setTranscript(text)}
          isTranscribing={isTranscribing}
          setIsTranscribing={setIsTranscribing}
        />

        <div className="input-group">
          <label className="label">Transcript</label>
          <textarea
            className="textarea"
            placeholder="Call transcript will appear here..."
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
          />
        </div>

        <button
          className="btn btn-primary"
          style={{ width: '100%' }}
          onClick={handleSubmit}
          disabled={!transcript || isProcessing}
        >
          {isProcessing ? 'Analyzing Call...' : 'Generate CRM Log'}
        </button>
      </div>

      <ResultDisplay result={result} title="CRM Suggestion" type="call" />
    </div>
  );
}

function EmailLogger() {
  const [instructions, setInstructions] = useState('');
  const [content, setContent] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!content) return;
    setIsProcessing(true);
    setResult(null);
    try {
      const response = await api.post('/log_email', {
        user_instructions: instructions,
        user_input: content
      });
      setResult(response.data);
    } catch (error) {
      console.error("Processing error", error);
      let msg = "Error processing email log";
      if (error.response) {
        msg += ` (Status ${error.response.status}): ${JSON.stringify(error.response.data)}`;
      } else {
        msg += `: ${error.message}`;
      }
      alert(msg);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Log Email</h2>
        <p className="text-muted mb-6">Draft an email based on your input (or recording) and instructions.</p>

        <TranscriptionControls
          onTranscribeComplete={(text) => setContent(text)}
          isTranscribing={isTranscribing}
          setIsTranscribing={setIsTranscribing}
        />

        <div className="input-group">
          <label className="label">Instructions (Tone, Goal, etc.)</label>
          <input
            className="input"
            placeholder="e.g. Professional, asking for a meeting..."
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
          />
        </div>

        <div className="input-group">
          <label className="label">Email Content / Draft</label>
          <textarea
            className="textarea"
            placeholder="Paste your rough draft or bullet points here..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>

        <button
          className="btn btn-primary"
          style={{ width: '100%' }}
          onClick={handleSubmit}
          disabled={!content || isProcessing}
        >
          {isProcessing ? 'Generating Email...' : 'Generate Email Log'}
        </button>
      </div>

      <ResultDisplay result={result} title="Generated Email" type="email" />
    </div>
  );
}

function TaskLogger() {
  const [description, setDescription] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!description) return;
    setIsProcessing(true);
    setResult(null);
    try {
      const response = await api.post('/log_task', { user_input: description });
      setResult(response.data);
    } catch (error) {
      console.error("Processing error", error);
      let msg = "Error processing task";
      if (error.response) {
        msg += ` (Status ${error.response.status}): ${JSON.stringify(error.response.data)}`;
      } else {
        msg += `: ${error.message}`;
      }
      alert(msg);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Log Task</h2>
        <p className="text-muted mb-6">Turn a rough task description (or recording) into a structured CRM task.</p>

        <TranscriptionControls
          onTranscribeComplete={(text) => setDescription(text)}
          isTranscribing={isTranscribing}
          setIsTranscribing={setIsTranscribing}
        />

        <div className="input-group">
          <label className="label">Task Description</label>
          <textarea
            className="textarea"
            style={{ minHeight: '80px' }}
            placeholder="e.g. Follow up with John regarding the contract..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <button
          className="btn btn-primary"
          style={{ width: '100%' }}
          onClick={handleSubmit}
          disabled={!description || isProcessing}
        >
          {isProcessing ? 'Processing Task...' : 'Generate Task Log'}
        </button>
      </div>

      <ResultDisplay result={result} title="Structured Task" type="task" />
    </div>
  );
}

function NextActionLogger() {
  const [transcript, setTranscript] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!transcript) return;
    setIsProcessing(true);
    setResult(null);
    try {
      const response = await api.post('/next_action', { user_input: transcript });
      setResult(response.data);
    } catch (error) {
      console.error("Processing error", error);
      let msg = "Error getting next actions";
      if (error.response) {
        msg += ` (Status ${error.response.status}): ${JSON.stringify(error.response.data)}`;
      } else {
        msg += `: ${error.message}`;
      }
      alert(msg);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card" style={{ borderColor: 'var(--color-accent)' }}>
        <h2 className="text-2xl font-bold mb-4">Get Next Actions</h2>
        <p className="text-muted mb-6">Analyze a conversation or text to determine the best next steps.</p>

        <TranscriptionControls
          onTranscribeComplete={(text) => setTranscript(text)}
          isTranscribing={isTranscribing}
          setIsTranscribing={setIsTranscribing}
        />

        <div className="input-group">
          <label className="label">Context / Transcript</label>
          <textarea
            className="textarea"
            placeholder="Paste call transcript or context here..."
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
          />
        </div>

        <button
          className="btn"
          style={{ width: '100%', backgroundColor: 'var(--color-accent)', color: 'var(--color-text)' }}
          onClick={handleSubmit}
          disabled={!transcript || isProcessing}
        >
          {isProcessing ? 'Thinking...' : 'Get Next Actions'}
        </button>
      </div>

      <ResultDisplay result={result} title="Recommended Actions" type="next_action" />
    </div>
  );
}

function ResultDisplay({ result, title, type }) {
  if (!result) return null;

  // Handle error case generically
  if (result.error) {
    return (
      <div className="card mt-6" style={{ marginTop: '2rem', borderColor: '#EF4444' }}>
        <h3 className="text-xl font-bold mb-2 text-red-600">Error</h3>
        <p>{result.comments || result.body || result.description || "An error occurred."}</p>
      </div>
    )
  }

  // Render specific component based on type
  return (
    <div className="card mt-6" style={{ marginTop: '2rem' }}>
      <h3 className="text-xl font-bold mb-4">{title}</h3>

      {type === 'call' && <CallResult result={result} />}
      {type === 'email' && <EmailResult result={result} />}
      {type === 'task' && <TaskResult result={result} />}
      {type === 'next_action' && <NextActionResult result={result} />}

      {!type && (
        <div className="bg-gray-50 p-4 rounded border">
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

function Badge({ children, color = 'gray' }) {
  return <span className={`badge badge-${color}`}>{children}</span>
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button className="copy-btn" onClick={handleCopy} title="Copy to clipboard">
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

function CallResult({ result }) {
  const callTypeColors = {
    'Color Match': 'blue',
    'Complaints': 'red',
    'Equipment Repair': 'yellow',
    'Line Audit': 'green',
    'Technical Support': 'blue',
    'Other': 'gray'
  };

  return (
    <div className="result-section">
      <div className="result-header">
        <div>
          <div className="result-title">{result.subject}</div>
          <Badge color={callTypeColors[result.call_type] || 'gray'}>{result.call_type}</Badge>
        </div>
      </div>

      <div className="result-grid-2">
        {result.name && (
          <div className="field-group">
            <div className="field-label">Contact Name</div>
            <div className="field-value">{result.name}</div>
          </div>
        )}
        {result.company && (
          <div className="field-group">
            <div className="field-label">Company</div>
            <div className="field-value">{result.company}</div>
          </div>
        )}
      </div>

      <div className="field-group">
        <div className="field-label">Comments</div>
        <div className="field-value pre-wrap">{result.comments}</div>
      </div>
    </div>
  );
}

function EmailResult({ result }) {
  return (
    <div className="result-section">
      <div className="field-group">
        <div className="field-label">To</div>
        <div className="field-value">{result.to?.join(', ') || '(Empty)'}</div>
      </div>

      {(result.cc?.length > 0) && (
        <div className="field-group">
          <div className="field-label">CC</div>
          <div className="field-value">{result.cc.join(', ')}</div>
        </div>
      )}

      <div className="field-group" style={{ marginTop: '1rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '1rem' }}>
        <div className="field-label">Subject</div>
        <div className="field-value font-bold">{result.subject}</div>
      </div>

      <div className="field-group" style={{ marginTop: '1rem' }}>
        <div className="flex items-center justify-between">
          <div className="field-label">Body</div>
          <CopyButton text={result.body} />
        </div>
        <div className="field-value pre-wrap bg-white p-4 border rounded" style={{ border: '1px solid var(--color-border)' }}>
          {result.body}
        </div>
      </div>
    </div>
  );
}

function TaskResult({ result }) {
  const priorityColors = { 'High': 'red', 'Medium': 'yellow', 'Low': 'blue' };
  const statusColors = { 'Open': 'blue', 'Completed': 'green', 'In Progress': 'yellow' };

  return (
    <div className="result-section">
      <div className="result-header">
        <div className="result-title">{result.subject}</div>
        <div className="flex gap-md">
          <Badge color={statusColors[result.status] || 'gray'}>{result.status}</Badge>
          <Badge color={priorityColors[result.priority] || 'gray'}>{result.priority}</Badge>
        </div>
      </div>

      <div className="result-grid-2">
        <div className="field-group">
          <div className="field-label">Due Date</div>
          <div className="field-value">{result.due_date || 'No Date'}</div>
        </div>
        <div className="field-group">
          <div className="field-label">Call Type</div>
          <div className="field-value">{result.call_type}</div>
        </div>
      </div>

      <div className="result-grid-2">
        {result.name && (
          <div className="field-group">
            <div className="field-label">Assigned To / Contact</div>
            <div className="field-value">{result.name}</div>
          </div>
        )}
        {result.company && (
          <div className="field-group">
            <div className="field-label">Company</div>
            <div className="field-value">{result.company}</div>
          </div>
        )}
      </div>

      <div className="field-group">
        <div className="field-label">Description</div>
        <div className="field-value pre-wrap">{result.comments}</div>
      </div>
    </div>
  );
}

function NextActionResult({ result }) {
  return (
    <div className="result-content">
      <div className="result-section">
        <div className="field-group">
          <div className="field-label">Strategic Goal</div>
          <div className="field-value font-bold text-xl">{result.goal}</div>
        </div>
        <div className="field-group mt-4">
          <div className="field-label">Summary</div>
          <div className="field-value">{result.summary}</div>
        </div>
      </div>

      <h4 className="font-bold mt-6 mb-2">Recommended Actions</h4>
      <div className="action-list">
        {result.next_actions?.map((action, idx) => (
          <div key={idx} className="action-card">
            <div className="action-header">
              <div className="font-bold">{action.action}</div>
              <Badge color={action.priority === 'High' ? 'red' : action.priority === 'Medium' ? 'yellow' : 'green'}>
                {action.priority}
              </Badge>
            </div>
            <div className="action-why">{action.why}</div>
            <div className="action-meta">
              <div>📅 Due: {action.due_date || 'None'}</div>
              <div>Outcome: {action.expected_outcome}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App
