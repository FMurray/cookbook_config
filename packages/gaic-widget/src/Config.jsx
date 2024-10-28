import * as React from 'react';
import { useModelState } from './app';
import { ReactFlow, ReactFlowProvider, Controls, Background, Handle, addEdge, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCallback, useState, useEffect } from 'react';

// Custom node component with handles
const CustomNode = ({ data, style }) => (
  <div style={{...style, padding: '10px'}}>
    <Handle 
      type="target" 
      position="left" 
      style={{ background: '#555' }}
    />
    <div>{data.label}</div>
    <Handle 
      type="source" 
      position="right" 
      style={{ background: '#555' }}
    />
  </div>
);

// Node types registration
const nodeTypes = {
  customNode: CustomNode
};

// Layout configuration
const layoutConfig = {
  'source': { x: 0, y: 0 },
  'step': { x: 300, y: 0 },
  'output': { x: 600, y: 0 }
};

// Node styles
const nodeStyles = {
  source: { border: '2px solid #4CAF50', background: 'white', borderRadius: '5px' },
  step: { border: '2px solid #2196F3', background: 'white', borderRadius: '5px' },
  output: { border: '2px solid #9C27B0', background: 'white', borderRadius: '5px' }
};

export default function ConfigWidget() {
  const [dataSources] = useModelState("data_sources");
  const [processingSteps] = useModelState("processing_steps");
  const [outputs] = useModelState("outputs");
  const [configEdges, setConfigEdges] = useModelState("edges");
  
  // Local state for React Flow
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState(configEdges);

  // Update local edges state when model edges change
  useEffect(() => {
    setEdges(configEdges);
  }, [configEdges]);

  const onNodesChange = useCallback(
    (changes) => {
      console.log('Node changes:', changes);
      setNodes((nds) => applyNodeChanges(changes, nds));
    },
    []
  );

  const onEdgesChange = useCallback(
    (changes) => {
      console.log('Edge changes:', changes);
      const updatedEdges = applyEdgeChanges(changes, edges);
      setEdges(updatedEdges);
      setConfigEdges(updatedEdges);
    },
    [edges, setConfigEdges]
  );

  const onConnect = useCallback(
    (params) => {
      console.log('Connection params:', params);
      const newEdge = {
        id: `edge-${params.source}-${params.target}`,
        source: params.source,
        target: params.target,
        type: 'smoothstep',
        style: { stroke: '#666', strokeWidth: 2 }
      };

      setEdges(currentEdges => {
        // Ensure currentEdges is an array
        const edgesArray = Array.isArray(currentEdges) ? currentEdges : [];
        
        // Check for existing connection
        if (!edgesArray.some(e => e.source === newEdge.source && e.target === newEdge.target)) {
          const updatedEdges = [...edgesArray, newEdge];
          console.log('New edges after connection:', updatedEdges);
          setConfigEdges(updatedEdges);
          return updatedEdges;
        }
        return edgesArray;
      });
    },
    [setConfigEdges]
  );

  // Transform nodes with custom node type
  useEffect(() => {
    const initialNodes = [
      ...dataSources.map((source, index) => ({
        id: source.id,
        type: 'customNode',
        position: { 
          x: layoutConfig.source.x, 
          y: layoutConfig.source.y + (index * 100) 
        },
        data: { label: source.label },
        style: nodeStyles.source
      })),
      ...processingSteps.map((step, index) => ({
        id: step.id,
        type: 'customNode',
        position: { 
          x: layoutConfig.step.x, 
          y: layoutConfig.step.y + (index * 100) 
        },
        data: { label: step.label },
        style: nodeStyles.step
      })),
      ...outputs.map((output, index) => ({
        id: output.id,
        type: 'customNode',
        position: { 
          x: layoutConfig.output.x, 
          y: layoutConfig.output.y + (index * 100) 
        },
        data: { label: output.label },
        style: nodeStyles.output
      }))
    ];
    setNodes(initialNodes);
  }, [dataSources, processingSteps, outputs]);

  // Transform edges for ReactFlow (visual properties only)
  const flowEdges = edges.map(edge => ({
    ...edge,
    type: 'smoothstep',
    style: { 
      stroke: '#666',
      strokeWidth: 2
    }
  }));

  return (
    <div style={{ 
      position: 'absolute', // Position relative to Jupyter cell
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      width: '100%',
      height: '100%'
  }}>
        <ReactFlow
          nodes={nodes}
          edges={flowEdges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          attributionPosition="bottom-left"
          defaultEdgeOptions={{
            type: 'smoothstep',
          }}
        >
          <Controls />
          <Background variant="dots" gap={12} size={1} />
        </ReactFlow>
    </div>
  );
}
