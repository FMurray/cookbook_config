import * as React from 'react';
import { useModel, useModelState } from '../../app';

export function useCatalogSchemas() {
  const model = useModel();
  const [schemas, setSchemas] = useModelState('schemas');

  React.useEffect(() => {
    
    function handleSchemaUpdate(msg) {
      if (msg.type === 'schema_update') {
        setSchemas(msg.schemas);
      }
    }
    
    model.on('msg:custom', handleSchemaUpdate);
    return () => model.off('msg:custom', handleSchemaUpdate);
  }, [model]);

  const requestSchemas = React.useCallback((catalogName) => {
    if (catalogName) {
      model.send({
        type: 'catalog_selected',
        catalog: catalogName
      });
    }
  }, [model]);

  return { schemas, requestSchemas };
} 