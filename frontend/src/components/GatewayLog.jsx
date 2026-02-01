import { useState, useRef, useEffect } from 'react';

/**
 * GatewayLog - Collapsible panel showing real-time Keywords AI gateway
 * LLM call activity and judge agent interactions.
 *
 * Props:
 *   calls      - Array of gateway_call events: {call_type, model, prompt_id, latency_ms, tokens_in, tokens_out, status, error?}
 *   judgeLogs   - Array of judge_verdict events: {detection_index, iteration, bbox, verdict, confidence, reasoning, corrected_bbox?}
 *   isActive    - Whether detection is currently running
 */
export default function GatewayLog({ calls = [], judgeLogs = [], isActive = false }) {
  const [collapsed, setCollapsed] = useState(true);
  const scrollRef = useRef(null);
  const hasAutoExpanded = useRef(false);

  // Auto-expand on first call
  useEffect(() => {
    if (calls.length > 0 && !hasAutoExpanded.current) {
      setCollapsed(false);
      hasAutoExpanded.current = true;
    }
  }, [calls.length]);

  // Auto-scroll to bottom when new entries arrive
  useEffect(() => {
    if (scrollRef.current && !collapsed) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [calls.length, judgeLogs.length, collapsed]);

  // Compute summary stats
  const totalCalls = calls.length;
  const totalLatency = calls.reduce((s, c) => s + (c.latency_ms || 0), 0);
  const totalTokens = calls.reduce((s, c) => s + (c.tokens_in || 0) + (c.tokens_out || 0), 0);

  const correctCount = judgeLogs.filter(l => l.verdict === 'CORRECT').length;
  const correctedCount = judgeLogs.filter(l => l.corrected_bbox).length;
  const removedCount = judgeLogs.filter(l => l.verdict === 'NOT_FOUND').length;

  const formatLatency = (ms) => {
    if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
    return `${ms}ms`;
  };

  const formatTokens = (n) => {
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
    return String(n);
  };

  // Build a merged timeline of calls + judge logs for display
  const entries = [];
  let callIdx = 0;
  let judgeIdx = 0;

  // Simple interleaving: gateway calls in order, with judge logs matched after judge calls
  for (let i = 0; i < calls.length; i++) {
    const call = calls[i];
    const entry = { type: 'call', index: i + 1, ...call };

    // If this is a judge call, attach the matching judge log
    if (call.call_type === 'judge' && judgeIdx < judgeLogs.length) {
      entry.judgeLog = judgeLogs[judgeIdx];
      judgeIdx++;
    }
    entries.push(entry);
  }

  if (totalCalls === 0) return null;

  return (
    <div className="bg-neutral-900 rounded-xl border border-neutral-800 mt-4">
      {/* Header */}
      <button
        onClick={() => setCollapsed(c => !c)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-800/50 rounded-xl transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-neutral-500 text-xs">{collapsed ? '▶' : '▼'}</span>
          <span className="text-sm font-medium text-neutral-200">Agent Gateway Log</span>
          {isActive && (
            <span className="inline-block w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          )}
        </div>
        <div className="flex items-center gap-3 text-xs text-neutral-500 font-mono">
          <span>{totalCalls} call{totalCalls !== 1 ? 's' : ''}</span>
          <span>{formatLatency(totalLatency)}</span>
          <span>{formatTokens(totalTokens)} tokens</span>
        </div>
      </button>

      {/* Body */}
      {!collapsed && (
        <div className="border-t border-neutral-800">
          <div
            ref={scrollRef}
            className="max-h-64 overflow-y-auto divide-y divide-neutral-800/50"
          >
            {entries.map((entry, i) => (
              <CallEntry key={i} entry={entry} formatLatency={formatLatency} formatTokens={formatTokens} />
            ))}
          </div>

          {/* Footer summary */}
          {judgeLogs.length > 0 && (
            <div className="border-t border-neutral-800 px-4 py-2.5 flex flex-wrap gap-x-4 gap-y-1 text-xs font-mono">
              <span className="text-neutral-400">Verdicts:</span>
              {correctCount > 0 && (
                <span className="text-green-400">{correctCount} correct</span>
              )}
              {correctedCount > 0 && (
                <span className="text-amber-400">{correctedCount} corrected</span>
              )}
              {removedCount > 0 && (
                <span className="text-red-400">{removedCount} removed</span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


function CallEntry({ entry, formatLatency, formatTokens }) {
  const isDetect = entry.call_type === 'detect';
  const isError = entry.status === 'error';
  const judgeLog = entry.judgeLog;

  // Determine verdict styling
  let verdictColor = 'text-neutral-400';
  let verdictIcon = '';
  if (judgeLog) {
    if (judgeLog.verdict === 'CORRECT') {
      verdictColor = 'text-green-400';
      verdictIcon = '✓';
    } else if (judgeLog.verdict === 'INCORRECT') {
      verdictColor = 'text-amber-400';
      verdictIcon = '⚠';
    } else if (judgeLog.verdict === 'NOT_FOUND') {
      verdictColor = 'text-red-400';
      verdictIcon = '✗';
    }
  }

  return (
    <div className="px-4 py-2.5">
      {/* Main row */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-neutral-600 text-xs font-mono w-6">#{entry.index}</span>

        {/* Type badge */}
        <span className={`text-xs font-mono px-1.5 py-0.5 rounded ${
          isDetect
            ? 'bg-blue-900/40 text-blue-400 border border-blue-800/50'
            : 'bg-amber-900/40 text-amber-400 border border-amber-800/50'
        }`}>
          {isDetect ? 'DETECT' : 'JUDGE'}
        </span>

        <span className="text-xs text-neutral-400 font-mono">{entry.model}</span>

        {entry.prompt_id && (
          <span className="text-xs text-neutral-600 font-mono">[{entry.prompt_id}]</span>
        )}

        <span className="text-xs text-neutral-300 font-mono ml-auto">
          {formatLatency(entry.latency_ms)}
        </span>

        {isError ? (
          <span className="text-xs text-red-400">✗ error</span>
        ) : judgeLog ? (
          <span className={`text-xs ${verdictColor}`}>
            {verdictIcon} {judgeLog.verdict}
          </span>
        ) : (
          <span className="text-xs text-green-400">✓ success</span>
        )}
      </div>

      {/* Token details */}
      <div className="flex items-center gap-3 mt-1 ml-8">
        <span className="text-xs text-neutral-600 font-mono">
          Tokens: {formatTokens(entry.tokens_in)} in → {formatTokens(entry.tokens_out)} out
        </span>

        {/* Judge details */}
        {judgeLog && judgeLog.verdict === 'CORRECT' && (
          <span className="text-xs text-neutral-500 font-mono">
            Bbox [{judgeLog.bbox?.join(',')}] conf: {judgeLog.confidence?.toFixed(2)}
          </span>
        )}
      </div>

      {/* Correction info */}
      {judgeLog?.corrected_bbox && (
        <div className="mt-1 ml-8 text-xs text-amber-400/80 font-mono">
          Corrected → [{judgeLog.corrected_bbox.join ? judgeLog.corrected_bbox.join(',') : `${judgeLog.corrected_bbox.x1},${judgeLog.corrected_bbox.y1},${judgeLog.corrected_bbox.x2},${judgeLog.corrected_bbox.y2}`}] → re-judging...
        </div>
      )}

      {/* NOT_FOUND info */}
      {judgeLog?.verdict === 'NOT_FOUND' && (
        <div className="mt-1 ml-8 text-xs text-red-400/80 font-mono">
          Detection removed
        </div>
      )}

      {/* Reasoning (truncated) */}
      {judgeLog?.reasoning && (
        <div className="mt-1 ml-8 text-xs text-neutral-600 truncate max-w-md" title={judgeLog.reasoning}>
          {judgeLog.reasoning}
        </div>
      )}

      {/* Error message */}
      {isError && entry.error && (
        <div className="mt-1 ml-8 text-xs text-red-400/80 truncate max-w-md" title={entry.error}>
          {entry.error}
        </div>
      )}
    </div>
  );
}
