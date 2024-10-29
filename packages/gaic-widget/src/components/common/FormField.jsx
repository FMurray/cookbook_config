import * as React from 'react';

export const FormField = ({ 
  label, 
  type = 'text', 
  value, 
  onChange, 
  options = [], 
  placeholder = '' 
}) => {
  return (
    <div className="form-field">
      <label>{label}</label>
      {type === 'select' ? (
        <select 
          value={value} 
          onChange={(e) => onChange(e.target.value)}
          className="form-select"
        >
          {options.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="form-input"
        />
      )}
    </div>
  );
}; 