export type Node = {
	id: number,
	title: any//string,
	label: string,
	color?: object,
	value?: number,
	chosen?: any
}

export type BarData ={
	FunctionName: string,
	StatType: string,
	Value: number
}

export type Edge = {
	from: number,
	to: number,
	value?: number,
	title?: string|number,
	label?: string
}

export type graphstate = {
	edges: Edge[]
	nodes: Node[]
};


type dateState = {
	from: number,
	fromGran: number,
	to: number,
	toGran: number
}

type bargraphstate = { //try it out
	data: ReadonlyArray<BarData>

}

export type applicationState = {
	requestArchitectureGraph: graphstate,
	architectureUsageGraph1: graphstate,
	architectureUsageGraph2: graphstate,
	startupGraph: graphstate,
	content: false | string,
	navigate: | boolean,
	datestate: dateState,
	barGraph: bargraphstate,
	pageView?: JSX.Element,
	availableDeploymentDocumentation: string[]
}

export type requestArgs = {
	arg1: number,
	arg2: number,
	arg3: false
} |
{	arg1: string,
	arg2: string,
	arg3: true}
