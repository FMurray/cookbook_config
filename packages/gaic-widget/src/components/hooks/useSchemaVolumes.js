import * as React from 'react';
import { useModel } from '../../app';

export function useSchemaVolumes() {
  const model = useModel();
  const [volumes, setVolumes] = React.useState([]);

  React.useEffect(() => {
    function handleVolumeUpdate(msg) {
      if (msg.type === 'volume_update') {
        setVolumes(msg.volumes);
      }
    }
    
    model.on('msg:custom', handleVolumeUpdate);
    return () => model.off('msg:custom', handleVolumeUpdate);
  }, [model]);

  const requestVolumes = React.useCallback((catalogName, schemaName) => {
    model.send({ type: 'volume_request', catalog: catalogName, schema: schemaName });
  }, [model]);

  return { volumes, requestVolumes };
}