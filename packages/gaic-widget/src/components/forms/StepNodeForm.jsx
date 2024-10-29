import * as React from 'react';
import { FormField } from '../common/FormField';

export const StepNodeForm = ({ data, onUpdate }) => {
  return (
    <div className="node-form">
      <FormField
        label="Step Name"
        value={data.label}
        onChange={(value) => onUpdate({ ...data, label: value })}
      />
      <FormField
        label="Operation"
        type="select"
        options={['filter', 'transform', 'join']}
        value={data.operation}
        onChange={(value) => onUpdate({ ...data, operation: value })}
      />
    </div>
  );
}; 