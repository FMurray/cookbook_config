import React, { useState } from 'react';
import { createRender } from '@anywidget/react';

const Widget = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>Count: {count}</h1>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
};

export default createRender(Widget);