export function keyOf<T>(key : keyof T & string) : string{
	return key;
}


export async function sendRequest(param1: number | string, param2: number | string, isDeploymentRequest:Boolean) {
	const apiFetcher = 'https://k9k78hhull.execute-api.us-east-1.amazonaws.com/Test/fetcher';
	const apiDeploymentDocs = 'https://3z85hqr2me.execute-api.us-east-1.amazonaws.com/test/fetchdeploymentdocs';
	var body;
	var api;

	if (isDeploymentRequest){
		if (param1 !== 'list'){
			//alert('The documentation will arrive momentarily...');
		}
		api = apiDeploymentDocs;
		body = {
			'type': param1,
			'key': param2
		}
	}
	else {
		//alert('The documentation will arrive momentarily...');
		api = apiFetcher
		body = {
			'from': param1,
			'to': param2,
			'flag': 'normal' //only the backend sends requests to the fetcher with something other than 'normal'
		}
	}

	const response = await fetch(api, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	})

	return response;
}