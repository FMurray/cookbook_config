import * as React from 'react';
import { useModelState } from './app';
import { ReactFlow, ReactFlowProvider, Controls, Background, Handle, addEdge, applyNodeChanges, applyEdgeChanges, Panel, ViewportPortal} from '@xyflow/react';
import { stratify, tree } from 'd3-hierarchy';
import '@xyflow/react/dist/style.css';
import { useCallback, useState, useEffect, useMemo } from 'react';
import { NodeDetails } from './components/NodeDetails';

// Custom node component with handles
const CustomNode = React.memo(({ data, style }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  console.log('CustomNode rendering with data:', data); // Debug log

  return (
    <div style={{ 
      ...style, 
      padding: '10px',
      width: isExpanded ? '300px' : '150px',
      transition: 'all 0.3s ease'
    }}>
      <Handle 
        type="target" 
        position="left" 
        style={{ background: '#555' }}
      />
      
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>{data.label}</div>
        <div style={{ display: 'flex', gap: '4px' }}>
          <button
            onClick={() => data.onEdit(data)}
            style={{
              background: 'transparent',
              border: '1px solid white',
              color: 'white',
              borderRadius: '3px',
              cursor: 'pointer',
              padding: '2px 6px'
            }}
          >
            ✎
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: 'transparent',
              border: '1px solid white',
              color: 'white',
              borderRadius: '3px',
              cursor: 'pointer',
              padding: '2px 6px'
            }}
          >
            {isExpanded ? '−' : '+'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div style={{
          marginTop: '10px',
          padding: '8px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '3px'
        }}>
          {data.type === 'source' && (
            <>
              <div>Catalog: {data.catalog || 'N/A'}</div>
              <div>Schema: {data.schema || 'N/A'}</div>
              <div>Volume: {data.volume_name || 'N/A'}</div>
              <div>Table: {data.table || 'N/A'}</div>
              <a 
                href={data.workspace_link} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{
                  color: '#fff',
                  textDecoration: 'underline',
                  cursor: 'pointer',
                  pointerEvents: 'all'
                }}
              >
                View in Workspace
              </a>
            </>
          )}
          {data.type === 'step' && (
            <>
              <div>Operation: {data.operation || 'N/A'}</div>
              <div>Parameters: {JSON.stringify(data.parameters) || 'None'}</div>
            </>
          )}
          {data.type === 'output' && (
            <>
              <div>Output Type: {data.outputType || 'N/A'}</div>
              <div>Destination: {data.destination || 'N/A'}</div>
            </>
          )}
        </div>
      )}

      <Handle 
        type="source" 
        position="right" 
        style={{ background: '#555' }}
      />
    </div>
  );
}, (prevProps, nextProps) => {
  // Return false if we should re-render
  return JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data);
});

// Layout configuration
const layoutConfig = {
  'source': { x: 100, y: 50 },
  'step': { x: 600, y: 50 },
  'output': { x: 1100, y: 50 }
};

// Node styles
const nodeStyles = {
  source: { 
    border: '2px solid #CD7F32', // Bronze
    background: 'linear-gradient(145deg, #CD7F32, #8B4513)',
    borderRadius: '5px',
    color: 'white'
  },
  step: { 
    border: '2px solid #C0C0C0', // Silver
    background: 'linear-gradient(145deg, #C0C0C0, #808080)',
    borderRadius: '5px',
    color: 'white'
  },
  output: { 
    border: '2px solid #FFD700', // Gold
    background: 'linear-gradient(145deg, #FFD700, #DAA520)',
    borderRadius: '5px',
    color: 'white'
  }
};

// Add layout helper function
const getLayoutedElements = (nodes, edges) => {
  // Group nodes by their parent
  const nodesByParent = nodes.reduce((acc, node) => {
    if (node.parentId) {
      if (!acc[node.parentId]) {
        acc[node.parentId] = [];
      }
      acc[node.parentId].push(node);
    }
    return acc;
  }, {});

  // Position nodes in a grid layout within their groups
  const layoutedNodes = nodes.map(node => {
    if (node.type === 'groupNode') {
      // Keep group nodes at their original positions
      return node;
    }

    const siblings = nodesByParent[node.parentId] || [];
    const indexInGroup = siblings.findIndex(n => n.id === node.id);
    const row = Math.floor(indexInGroup / 2);
    const col = indexInGroup % 2;

    return {
      ...node,
      position: {
        x: col * 200,  // 200px horizontal spacing between nodes
        y: row * 120   // 120px vertical spacing between rows
      }
    };
  });

  return { nodes: layoutedNodes, edges };
};

// Wrap the ConfigWidget component with ReactFlowProvider
export default function ConfigWidgetWrapper() {
  return (
    <ReactFlowProvider>
      <ConfigWidget />
    </ReactFlowProvider>
  );
}

// Rename the existing component to ConfigWidget (without default export)
function ConfigWidget() {
  const [dataSources] = useModelState("data_sources");
  const [processingSteps] = useModelState("processing_steps");
  const [outputs] = useModelState("outputs");
  const [configEdges, setConfigEdges] = useModelState("edges");
  
  // Local state for React Flow
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState(configEdges);
  const [selectedNode, setSelectedNode] = useState(null);


  const GroupNode = ({ data }) => {
    return (
      <div style={{
        padding: '20px',
        background: 'rgba(0, 0, 0, 0.3)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '8px',
        minWidth: '400px',
        minHeight: '200px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{ 
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '8px'
        }}>
          <div style={{ color: 'white', fontSize: '16px' }}>{data.label}</div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedNode(data.label === 'Data Sources' ? 'source' : 
                             data.label === 'Processing Steps' ? 'step' : 
                             'output');
            }}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              color: 'white',
              padding: '6px 12px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            + Add {data.label.slice(0, -1)}
          </button>
        </div>
      </div>
    );
  };

  const nodeTypes = useMemo(() => ({
    groupNode: GroupNode,
    customNode: CustomNode
  }), []);  // Empty dependency array since GroupNode is now defined inside

  const handleNodeClick = (event, node) => {
    // Skip group nodes
    if (node.type === 'groupNode') {
      return;
    }
    setSelectedNode(node);
  };

  const handleNodeUpdate = (nodeId, newData) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...newData } }
          : node
      )
    );
  };

  const handleSaveNode = (nodeId, newData) => {
    console.log('Saving node:', nodeId, newData);
    // Implement save logic here
  };

  // Update local edges state when model edges change
  useEffect(() => {
    setEdges(configEdges);
  }, [configEdges]);

  const onNodesChange = useCallback(
    (changes) => {
      console.log('Node changes:', changes);
      setNodes((nds) => applyNodeChanges(changes, nds));
    },
    [setNodes]
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
    console.log('Creating new nodes with updated data sources');
    const groupNodes = [
      {
        id: 'sources-group',
        type: 'groupNode',
        position: { x: layoutConfig.source.x, y: layoutConfig.source.y },
        data: { 
          label: 'Data Sources',
          onClick: createNewDataSource
        }
      },
      {
        id: 'steps-group',
        type: 'groupNode',
        position: { x: layoutConfig.step.x, y: layoutConfig.step.y },
        data: { 
          label: 'Processing Steps',
          onClick: createNewProcessingStep
        }
      },
      {
        id: 'outputs-group',
        type: 'groupNode',
        position: { x: layoutConfig.output.x, y: layoutConfig.output.y },
        data: { 
          label: 'Outputs',
          onClick: createNewOutput
        }
      }
    ];

    // Create completely new node objects
    const sourceNodes = dataSources.map((source, index) => {
      const nodeData = {
        label: source.label,
        type: 'source',
        catalog: source.catalog,
        schema: source.schema,
        table: source.table,
        volume_name: source.volume_name,
        workspace_link: source.workspace_link,
        onEdit: (nodeData) => setSelectedNode(nodeData)
      };

      return {
        id: source.id,
        type: 'customNode',
        parentId: 'sources-group',
        position: { x: 25, y: (index * 100) + 50 },
        data: nodeData,
        style: nodeStyles.source
      };
    });

    const stepNodes = processingSteps.map((step, index) => ({
      id: step.id,
      type: 'customNode',
      parentId: 'steps-group',
      position: { x: 25, y: (index * 100) + 50 },
      data: { 
        label: step.label,
        type: 'step',
        operation: step.operation,
        parameters: step.parameters,
        onEdit: (nodeData) => setSelectedNode(nodeData)
      },
      style: nodeStyles.step
    }));

    const outputNodes = outputs.map((output, index) => ({
      id: output.id,
      type: 'customNode',
      parentId: 'outputs-group',
      position: { x: 25, y: (index * 100) + 50 },
      data: { 
        label: output.label,
        type: 'output',
        outputType: output.outputType,
        destination: output.destination,
        onEdit: (nodeData) => setSelectedNode(nodeData)
      },
      style: nodeStyles.output
    }));

    // Create a completely new array of nodes
    const newNodes = [
      ...groupNodes,
      ...sourceNodes,
      ...stepNodes,
      ...outputNodes
    ];

    console.log('Setting completely new nodes:', newNodes);
    
    // Force React Flow to update by setting nodes to empty first
    setNodes([]);
    setTimeout(() => setNodes(newNodes), 0);

  }, [dataSources, processingSteps, outputs]);

  // Apply layout when nodes or edges change
  useEffect(() => {
    if (nodes.length > 0) {
      const { nodes: layoutedNodes } = getLayoutedElements(nodes, edges);
      setNodes(layoutedNodes);
    }
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

  // Add these new functions
  const createNewDataSource = useCallback(() => {
    const newId = `source-${Date.now()}`;
    const newNode = {
      id: newId,
      type: 'customNode',
      parentId: 'sources-group',
      position: { x: 25, y: (dataSources.length * 100) + 50 },
      data: { 
        label: 'New Source',
        type: 'source',
        catalog: '',
        schema: '',
        table: '',
        workspace_link: ''
      },
      style: nodeStyles.source
    };
    setNodes(nodes => [...nodes, newNode]);
  }, [dataSources.length]);

  const createNewProcessingStep = useCallback(() => {
    const newId = `step-${Date.now()}`;
    const newNode = {
      id: newId,
      type: 'customNode',
      parentId: 'steps-group',
      position: { x: 25, y: (processingSteps.length * 100) + 50 },
      data: { 
        label: 'New Step',
        type: 'step',
        operation: '',
        parameters: {}
      },
      style: nodeStyles.step
    };
    setNodes(nodes => [...nodes, newNode]);
  }, [processingSteps.length]);

  const createNewOutput = useCallback(() => {
    const newId = `output-${Date.now()}`;
    const newNode = {
      id: newId,
      type: 'customNode',
      parentId: 'outputs-group',
      position: { x: 25, y: (outputs.length * 100) + 50 },
      data: { 
        label: 'New Output',
        type: 'output',
        outputType: '',
        destination: ''
      },
      style: nodeStyles.output
    };
    setNodes(nodes => [...nodes, newNode]);
  }, [outputs.length]);

  // Add this effect to track dataSources changes
  useEffect(() => {
    console.log('DataSources updated:', dataSources);
  }, [dataSources]);

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={flowEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <Background />
          {selectedNode && <Panel position="bottom-center">
            <NodeDetails
              selectedNode={selectedNode}
              onUpdate={handleNodeUpdate}
              onClose={() => setSelectedNode(null)}
            />
          </Panel>}
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}
