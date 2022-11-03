<script>
import { getByID } from "node-movie";

let userid = '';
let RecMoviesJson = '';
let imdbIDList = [];
let recMovieInfoList = [];

async function getRecMovies() {
	let res = await fetch(`./movie?userid=${userid}`);
	RecMoviesJson = await res.text();
	imdbIDList = JSON.parse(RecMoviesJson);
	recMovieInfoList = [];

	console.log(imdbIDList);

	for (const id of imdbIDList){
		let tempID = id
		let paddedID = tempID.toString().padStart(7, '0');

		await getByID("tt" + paddedID, data => {
			recMovieInfoList = [...recMovieInfoList, data];
		});
	}
}

</script>

<input type="text" placeholder="enter userID" bind:value={userid} />
<button on:click={getRecMovies}>Predict</button>
{#each recMovieInfoList as {Title, Poster}, i }
	<li>
		<img src={Poster} alt="Movie Poster"/>
		<div>{i+1}. {Title}</div>
	</li>
{/each}