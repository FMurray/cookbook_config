import * as React from 'react';
import { SourceNodeForm } from './forms/SourceNodeForm';
import { StepNodeForm } from './forms/StepNodeForm';

export function NodeDetails({ selectedNode, onUpdate, onClose }) {
  console.log('Selected Node:', selectedNode);

  const getFormComponent = (node) => {
    switch (node?.type) {
      case 'source':
        return <SourceNodeForm data={node} onUpdate={onUpdate} />;
      case 'step':
        return <StepNodeForm data={node} onUpdate={onUpdate} />;
      case 'output':
        return <h3>Output Form (Coming Soon)</h3>;
      default:
        return <h3>Select a node type</h3>;
    }
  };

  return (
    <div style={{
      background: '#2a2a2a',
      padding: '20px',
      borderRadius: '4px',
      color: 'white'
    }}>
      {getFormComponent(selectedNode)}
    </div>
  );
} 