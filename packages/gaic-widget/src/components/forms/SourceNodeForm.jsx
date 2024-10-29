import * as React from 'react';

import { FormField } from '../common/FormField';

export const SourceNodeForm = ({ data, onUpdate }) => {
  return (
    <div className="node-form">
      <FormField
        label="Source Name"
        value={data.label}
        onChange={(value) => onUpdate({ ...data, label: value })}
      />
      <FormField
        label="Source Type"
        type="select"
        options={['Volume', 'Delta Table']}
        value={data.sourceType}
        onChange={(value) => onUpdate({ ...data, sourceType: value })}
      />
    </div>
  );
}; 