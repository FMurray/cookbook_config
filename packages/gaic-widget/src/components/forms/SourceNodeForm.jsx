import * as React from 'react';
import { useState } from 'react';
import { useModelState, useModel } from '../../app';
import { FormField } from '../common/FormField';
import { useCatalogSchemas } from '../hooks/useCatalogSchemas';
import { useSchemaVolumes } from '../hooks/useSchemaVolumes';

export const SourceNodeForm = ({ data, onUpdate }) => {
  const [catalogs] = useModelState('catalogs');
  const { schemas, requestSchemas } = useCatalogSchemas();
  const [selectedSchema, setSelectedSchema] = useState(data.schema || '');
  const [customSchema, setCustomSchema] = useState('');
  const [selectedVolume, setSelectedVolume] = useState(data.volume_name || '');
  const model = useModel();
  const { volumes, requestVolumes } = useSchemaVolumes();

  // Request schemas when catalog changes
  const handleCatalogChange = (value) => {
    console.log('Catalog changed to:', value);
    requestSchemas(value);
    onUpdate({ ...data, catalog: value });
  };

  // Handle schema selection changes
  const handleSchemaChange = (value) => {
    if (value === 'Custom') {
      setSelectedSchema('');
      onUpdate({ ...data, schema: '' });
    } else {
      setSelectedSchema(value);
      onUpdate({ ...data, schema: value });
      // Request volumes when schema changes
      if (data.catalog && value) {
        requestVolumes(data.catalog, value);
      }
    }
  };

  // Handle custom schema input
  const handleCustomSchemaChange = (value) => {
    setCustomSchema(value);
    onUpdate({ ...data, schema: value });
  };

  // Request schemas when component mounts if we have a catalog
  React.useEffect(() => {
    if (data.catalog) {
      requestSchemas(data.catalog);
    }
  }, []);

  // Request volumes when component mounts if we have a catalog and schema
  React.useEffect(() => {
    if (data.catalog && data.schema) {
      requestVolumes(data.catalog, data.schema);
    }
  }, []);

  // Update volume request handler to use catalog and schema
  const handleVolumeRequest = (catalog, schema) => {
    console.log('Requesting volumes for', catalog, schema);
    model.send({ 
      type: 'volume_request', 
      catalog: catalog,
      schema: schema 
    });
  };

  const handleSave = () => {
    console.log('Saving form data:', data);
    model.send({
      type: 'save_source_node',
      data: {
        ...data,
        schema: selectedSchema === 'Custom' ? customSchema : selectedSchema
      }
    });
  };

  return (
    <div className="node-form">
      <h3>{data.label}</h3>
      <FormField
        label="Catalog"
        type="select"
        options={catalogs}
        value={data.catalog}
        onChange={handleCatalogChange}
      />
      <FormField
        label="Schema"
        type="select"
        options={[...(schemas || []), 'Custom']}
        value={selectedSchema || 'Custom'}
        onChange={handleSchemaChange}
      />
      {(selectedSchema === '' || selectedSchema === 'Custom') && (
        <FormField
          label="Custom Schema"
          value={customSchema}
          onChange={handleCustomSchemaChange}
        />
      )}
      <FormField
        label="Volume"
        type="select"
        options={[...new Set([...volumes, data.volume_name].filter(Boolean))]}
        value={data.volume_name}
        onChange={(value) => onUpdate({ ...data, volume_name: value })}
      />
      <button 
        className="save-button" 
        onClick={handleSave}
        disabled={!data.catalog || (!selectedSchema && !customSchema)}
      >
        Save
      </button>
    </div>
  );
}; 