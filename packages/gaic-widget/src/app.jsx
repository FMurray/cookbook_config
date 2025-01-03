import * as React from "react";
import * as ReactDOM from "react-dom/client";
import '@xyflow/react/dist/style.css';

import ConfigWidget from "./Config";
import ConfigWidgetWrapper from "./Config";

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

export default { render: createRender(ConfigWidgetWrapper) };
