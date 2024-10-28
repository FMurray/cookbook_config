// import * as d3 from "https://esm.sh/litegraph.js@0.7";
import { LGraph, LGraphCanvas, LiteGraph } from "https://esm.sh/litegraph.js@0.7";
import "https://esm.sh/litegraph.js@0.7/css/litegraph.css" assert { type: "css" };

export function render({ model, el }) {
    // Clear any existing content
    el.innerHTML = '';
    el.className = 'config-widget';

    // Create title
    const title = document.createElement('h2');
    title.textContent = model.get("display_name");
    el.appendChild(title);

    // Create canvas for LiteGraph
    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 600;
    el.appendChild(canvas);

    // Initialize graph
    const graph = new LGraph();
    const graphCanvas = new LGraphCanvas(canvas, graph);

    // Disable zoom and drag
    graphCanvas.allow_dragcanvas = false;
    graphCanvas.allow_mousewheel = false;  // Disables mouse wheel zoom

    LGraphCanvas.prototype.onMouseWheel = function(event) {
        return;
    };

    // Configure graph settings
    graph.configure({
        align_to_grid: true,
        horizontal: true,  // Makes the graph flow left to right
        snap_size: 10,    // Grid size
        default_link_color: "#666",
        canvas_fill_color: "#ffffff"
    });

    // Register node types
    class DataSourceNode {
        constructor() {
            this.addOutput("output", "");
            this.shape = LiteGraph.BOX_SHAPE;
            this.color = "#4CAF50";
            this.size = [120, 40];  // Set node size
        }
    }
    LiteGraph.registerNodeType("pipeline/datasource", DataSourceNode);

    class ProcessingStepNode {
        constructor() {
            this.addInput("input", "");
            this.addOutput("output", "");
            this.shape = LiteGraph.BOX_SHAPE;
            this.color = "#2196F3";
            this.size = [120, 40];
        }
    }
    LiteGraph.registerNodeType("pipeline/step", ProcessingStepNode);

    class OutputNode {
        constructor() {
            this.addInput("input", "");
            this.shape = LiteGraph.BOX_SHAPE;
            this.color = "#9C27B0";
            this.size = [120, 40];
        }
    }
    LiteGraph.registerNodeType("pipeline/output", OutputNode);

    // Create nodes from model data
    const nodeMap = new Map();
    
    // Add data sources
    model.get("data_sources").forEach((source, index) => {
        const node = LiteGraph.createNode("pipeline/datasource");
        node.pos = [100, 100 + index * 100];
        node.title = source.label;
        node.id = source.id;  // Store the id for reference
        graph.add(node);
        nodeMap.set(source.id, node);
    });

    // Add processing steps
    model.get("processing_steps").forEach((step, index) => {
        const node = LiteGraph.createNode("pipeline/step");
        node.pos = [400, 100 + index * 100];
        node.title = step.label;
        node.id = step.id;
        graph.add(node);
        nodeMap.set(step.id, node);
    });

    // Add outputs
    model.get("outputs").forEach((output, index) => {
        const node = LiteGraph.createNode("pipeline/output");
        node.pos = [700, 100 + index * 100];
        node.title = output.label;
        node.id = output.id;
        graph.add(node);
        nodeMap.set(output.id, node);
    });

    // Create connections
    model.get("edges").forEach(edge => {
        const sourceNode = nodeMap.get(edge.source);
        const targetNode = nodeMap.get(edge.target);
        if (sourceNode && targetNode) {
            sourceNode.connect(0, targetNode, 0);
        }
    });

    // Add node selection handler
    graph.onNodeSelected = (node) => {
        const nodeData = [...model.get("data_sources"), 
                         ...model.get("processing_steps"),
                         ...model.get("outputs")]
            .find(d => d.label === node.title);
        
        if (nodeData) {
            model.set("selected", nodeData);
            model.save_changes();
        }
    };

    graphCanvas.setZoom(1);
    graphCanvas.align_to_grid = true;

    // Start the graph
    graph.start();
    graphCanvas.draw(true, true);
}

export default { render };
