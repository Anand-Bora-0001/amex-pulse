/**
 * AmEx Pulse — Journey Explorer Page
 * =====================================
 * Visual journey mapping with React Flow graph and journey list.
 */

import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Map, List, GitBranch } from 'lucide-react';
import { journeyApi, customerApi } from '../../lib/api';
import type { Journey, JourneyGraphResponse, Customer } from '../../types';

export default function JourneyExplorerPage() {
  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedJourney, setSelectedJourney] = useState<Journey | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [graphLoading, setGraphLoading] = useState(false);
  const [view, setView] = useState<'list' | 'graph'>('list');
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [journeysRes, customersRes] = await Promise.all([
        journeyApi.list({ limit: 50 }),
        customerApi.list({ page_size: 50 }),
      ]);
      setJourneys(journeysRes.data);
      setCustomers(customersRes.data.customers);
    } catch (err) {
      console.error('Failed to load journeys:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadGraph = async (journeyId: string) => {
    setGraphLoading(true);
    try {
      const res = await journeyApi.getGraph(journeyId);
      const data: JourneyGraphResponse = res.data;

      // Convert to React Flow nodes
      const typePositions: Record<string, { x: number; baseY: number; index: number }> = {
        customer: { x: 50, baseY: 200, index: 0 },
        channel: { x: 350, baseY: 50, index: 0 },
        journey: { x: 350, baseY: 400, index: 0 },
        event: { x: 650, baseY: 30, index: 0 },
        step: { x: 650, baseY: 350, index: 0 },
      };

      const flowNodes: Node[] = data.nodes.map((n) => {
        const pos = typePositions[n.type] || { x: 400, baseY: 200, index: 0 };
        const y = pos.baseY + pos.index * 80;
        pos.index += 1;
        return {
          id: n.id,
          type: n.type,
          position: { x: pos.x, y },
          data: { label: n.label, ...n.data },
        };
      });

      const flowEdges: Edge[] = data.edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        animated: e.animated,
        style: { stroke: '#006FCF', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#006FCF' },
        labelStyle: { fill: 'var(--text-muted)', fontSize: 10 },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
      setView('graph');
    } catch (err) {
      console.error('Failed to load graph:', err);
    } finally {
      setGraphLoading(false);
    }
  };

  const getCustomerName = (customerId: string): string => {
    const c = customers.find((c) => c.id === customerId);
    return c ? `${c.first_name} ${c.last_name}` : 'Unknown';
  };

  const statusColors: Record<string, string> = {
    completed: '#10B981',
    in_progress: '#3B82F6',
    failed: '#EF4444',
    abandoned: '#F59E0B',
  };

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Journey Explorer
          </h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {journeys.length} journeys • Visualize cross-channel customer journeys
          </p>
        </div>
        <div className="flex rounded-lg overflow-hidden" style={{ border: '1px solid var(--border-color)' }}>
          <button
            onClick={() => setView('list')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
              view === 'list' ? 'bg-blue-600 text-white' : ''
            }`}
            style={view !== 'list' ? { background: 'var(--bg-card)', color: 'var(--text-secondary)' } : {}}
          >
            <List size={16} /> List
          </button>
          <button
            onClick={() => { if (selectedJourney) loadGraph(selectedJourney.id); else setView('graph'); }}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
              view === 'graph' ? 'bg-blue-600 text-white' : ''
            }`}
            style={view !== 'graph' ? { background: 'var(--bg-card)', color: 'var(--text-secondary)' } : {}}
          >
            <GitBranch size={16} /> Graph
          </button>
        </div>
      </div>

      {view === 'list' ? (
        /* Journey List */
        <div className="space-y-3">
          {loading ? (
            <div className="text-center py-20">
              <div className="w-10 h-10 border-3 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto" />
            </div>
          ) : (
            journeys.map((journey) => (
              <div
                key={journey.id}
                className="stat-card cursor-pointer"
                onClick={() => {
                  setSelectedJourney(journey);
                  loadGraph(journey.id);
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ background: statusColors[journey.status] || '#6B7280' }}
                    />
                    <div>
                      <div className="flex items-center gap-3">
                        <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                          {journey.journey_type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                        </p>
                        <span
                          className="px-2 py-0.5 rounded-full text-[10px] font-semibold capitalize"
                          style={{
                            background: `${statusColors[journey.status] || '#6B7280'}20`,
                            color: statusColors[journey.status] || '#6B7280',
                          }}
                        >
                          {journey.status.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                        {getCustomerName(journey.customer_id)} • Intent: {journey.detected_intent?.replace(/_/g, ' ')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-mono font-bold" style={{ color: 'var(--text-primary)' }}>
                        {journey.progress.toFixed(0)}%
                      </p>
                      <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>progress</p>
                    </div>
                    <div className="w-24 h-2 rounded-full" style={{ background: 'var(--border-color)' }}>
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${journey.progress}%`,
                          background: statusColors[journey.status] || '#6B7280',
                        }}
                      />
                    </div>
                  </div>
                </div>
                {/* Steps preview */}
                {journey.steps.length > 0 && (
                  <div className="flex items-center gap-1 mt-3 overflow-x-auto">
                    {journey.steps.map((step, i) => (
                      <div key={step.id} className="flex items-center">
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-medium whitespace-nowrap"
                          style={{
                            background: step.step_status === 'completed' ? '#10B98115' :
                                        step.step_status === 'failed' ? '#EF444415' : 'var(--bg-primary)',
                            color: step.step_status === 'completed' ? '#10B981' :
                                   step.step_status === 'failed' ? '#EF4444' : 'var(--text-muted)',
                          }}
                        >
                          {step.step_name}
                        </span>
                        {i < journey.steps.length - 1 && (
                          <span className="mx-1 text-gray-400">→</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        /* Graph View */
        <div className="stat-card" style={{ height: '70vh', padding: 0, overflow: 'hidden' }}>
          {graphLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-10 h-10 border-3 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-3" />
                <p style={{ color: 'var(--text-muted)' }}>Loading journey graph...</p>
              </div>
            </div>
          ) : nodes.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <GitBranch size={40} className="mx-auto mb-3 text-gray-400" />
                <p style={{ color: 'var(--text-muted)' }}>Select a journey from the list to visualize its graph</p>
              </div>
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              fitView
              attributionPosition="bottom-left"
            >
              <Background color="var(--border-color)" gap={20} />
              <Controls />
              <MiniMap
                nodeColor={(n) => {
                  if (n.type === 'customer') return '#006FCF';
                  if (n.type === 'journey') return '#F7B731';
                  if (n.type === 'channel') return '#10B981';
                  return '#6B7280';
                }}
                style={{ background: 'var(--bg-card)' }}
              />
            </ReactFlow>
          )}
        </div>
      )}
    </div>
  );
}
