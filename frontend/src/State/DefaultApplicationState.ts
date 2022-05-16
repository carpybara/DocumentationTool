import { applicationState } from "../ApplicationModel/ApplicationState.model";

export const defaultState: applicationState = {
	content: false,
	navigate: false,
	requestArchitectureGraph: {
		edges: [{ from: 0, to: 0 }],
		nodes: [{
			id: 0,
			title: "",
			label: ""
		}]
	},
	architectureUsageGraph1: {
		edges: [{ from: 0, to: 0 }],
		nodes: [{
			id: 0,
			title: "",
			label: "",
			color: { background: "rgba(210, 229, 255,1)" }
		}]
	},
	architectureUsageGraph2: {
		edges: [{ from: 0, to: 0 }],
		nodes: [{
			id: 0,
			title: "",
			label: "",
		}]
	},
	startupGraph: {
		edges: [{ from: 0, to: 0 }],
		nodes: [{
			id: 0,
			title: "",
			label: "",
		}]
	},
	datestate: {
		from: 0,
		fromGran: 0,
		to: 	0,
		toGran: 0

	},
	barGraph: {
		data: []
	},
	availableDeploymentDocumentation: []
};