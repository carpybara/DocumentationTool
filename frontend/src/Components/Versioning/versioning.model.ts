export type inputType = {
	funcName: string,
	version : string,
	timestamps : number[],

}
export type outputType = {
	funcName: string,
	version : string,
	timestamps : ReadonlyArray<orderedTimes>,
}

export type orderedTimes = {
	version: string,
	timeRange: Date|string,
	value: number
}

