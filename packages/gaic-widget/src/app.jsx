import * as React from "react";
import * as ReactDOM from "react-dom/client";
import { ReactFlow, ReactFlowProvider, Controls, Background, Handle, addEdge, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import ConfigWidget from "./Config";

let RenderContext = React.createContext(null);

function useRenderContext() {
    let ctx = React.useContext(RenderContext);
    if (!ctx) throw new Error("RenderContext not found");
    return ctx;
}

export function useModel() {
    let ctx = useRenderContext();
    return ctx.model;
}

export function useModelState(key) {
    let model = useModel();
    let [value, setValue] = React.useState(model.get(key));
    React.useEffect(() => {
        let callback = () => setValue(model.get(key));
        model.on(`change:${key}`, callback);
        return () => model.off(`change:${key}`, callback);
    }, [model, key]);
    return [
        value,
        (value) => {
            model.set(key, value);
            model.save_changes();
        },
    ];
}

export function createRender(Widget) {
    return ({ el, model, experimental }) => {

      el.style.width = '100%';
      el.style.height = '600px';
      el.style.position = 'relative';  // Important for establishing stacking context
      el.style.display = 'block';      // Ensures proper block formatting context

      let root = ReactDOM.createRoot(el);
      root.render(
          <React.StrictMode>
              <RenderContext.Provider value={{ model, experimental }}>
                <Widget />
              </RenderContext.Provider>
          </React.StrictMode>
      );
      return () => root.unmount();
    };
}

export default { render: createRender(ConfigWidget) };
