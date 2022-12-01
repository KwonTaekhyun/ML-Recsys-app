<script>
import { getByID } from "node-movie";
import { onMount } from 'svelte';
import Button, { Label } from '@smui/button';
import { push } from 'svelte-spa-router';
import { isLoading } from '../store';
import CircularProgress from '@smui/circular-progress';
import { fade } from 'svelte/transition';

export let params = {};

let RecMoviesJson = '';
let imdbIDList = [];
let recMovieInfoList = [];



async function getRecMovies() {	
	isLoading.update(() => true);

	let res = await fetch(`./movie?userid=${params.userid}`);

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

	isLoading.update(() => false);
}

function goMain() {
	push('/')
}

onMount(async () => {
    getRecMovies()
});

</script>

<div class="board" in:fade out:fade>
	{#if $isLoading}
        <div class="loading" in:fade out:fade>
            <CircularProgress
                style="height: 32px; width: 32px;"
                color="primary"
                indeterminate
            />
        </div>
    {/if}
	<div class="recommendationList">
		{#each recMovieInfoList as {Title, Poster}, i }
			<div class="recommendation">
				<div class="movieName">{i+1}. {Title}</div>
				<img src={Poster} alt="Movie Poster"/>
			</div>
		{/each}
	</div>
	<div class="links">
        <Button
            on:click={goMain}
            variant="outlined"
        >
            <Label>Back</Label>
        </Button>
    </div>
</div>

<style lang="css">
    .board {
        width: 100%;
		text-align: center;
		padding-top: 50px;
    }

	.recommendationList{
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
	}

	.recommendation{
		width: 500px;
		margin-bottom: 20px;
	}

	.movieName{
		margin-bottom: 12px;
	}

	img{
		width: 200px;
	}

	.loading {
        position: absolute;
        top: 0px;
        z-index: 1;
        background: rgba(0, 0, 0, 0.5);
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>