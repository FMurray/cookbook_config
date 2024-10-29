// Create a forms directory with specific form components for each node type
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
        options={['delta_table', 'csv', 'json']}
        value={data.sourceType}
        onChange={(value) => onUpdate({ ...data, sourceType: value })}
      />
      {/* Additional fields based on source type */}
    </div>
  );
};

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
      {/* Dynamic fields based on operation type */}
    </div>
  );
}; 