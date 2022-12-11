<script>
import { onMount } from 'svelte';
import Select, { Option } from '@smui/select';
import Button, { Label } from '@smui/button';
import { push } from 'svelte-spa-router';
import { isLoading } from '../store';
import CircularProgress from '@smui/circular-progress';
import { fade } from 'svelte/transition';

let MoviesJson = '';
let Movies = {};
let GenresJson = '';
let Genres = [];
const Ratings = ['0.0', '0.5', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0'];

let NewUserIdJson = '';
let NewUserId = '';

let new_rating_list = [];

function addNewRating() {
    new_rating_list = [...new_rating_list, {
        genre: '(no genres listed)',
        movieId: '0',
        rating: '0.0',
    }]
}

async function getInfo() {
	let res = await fetch(`./movies_by_genre`);
	MoviesJson = await res.text();
	Movies = JSON.parse(MoviesJson);

    let res2 = await fetch(`./geres`);
	GenresJson = await res2.text();
	Genres = JSON.parse(GenresJson);

    let res3 = await fetch(`./new_user_id`);
	NewUserIdJson = await res3.text();
	NewUserId = JSON.parse(NewUserIdJson);

    console.log('new user id: ' + NewUserId);

    addNewRating();
}

async function addRatings() {
    isLoading.update(() => true);

    console.log(new_rating_list);

    const new_ratings = new FormData();

    new_rating_list.forEach((new_rating) => {
        new_ratings.append('newRatings', JSON.stringify(new_rating))
    })
    
	await fetch(`./ratings`, {
        method: 'POST',
        body: new_ratings,
    }).then((response) => {
        isLoading.update(() => false);
        console.log(response.text())
    }).then(() => {
        push('/rec/'+ NewUserId)
    }).catch((error) => console.log(error));
}

onMount(async () => {
    getInfo()
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
    <div>
        {#each new_rating_list as new_rating}
            <div class="addRating">
                <div>
                    <Select
                        key={(Genre) => `${Genre ? Genre : ''}`}
                        bind:value={new_rating['genre']}
                        label="Genre"
                    >
                        {#each Genres as Genre}
                            <Option value={Genre}>{Genre}</Option>
                        {/each}
                    </Select>
                </div>
                <div class="movie">
                    <Select
                        key={(Movie) => `${Movie ? Movie['movieId'] : '0'}`}
                        bind:value={new_rating['movieId']}
                        label="Movie"
                        style="min-width: 250px"
                    >
                        {#each Movies[new_rating['genre']] as Movie}
                            <Option value={Movie['movieId']} style="min-width: 200px">{Movie['title']}</Option>
                        {/each}
                    </Select>
                </div>
                <div>
                    <Select
                        key={(Rating) => `${Rating ? Rating : '0.0'}`}
                        bind:value={new_rating['rating']}
                        label="Rating"
                    >
                        {#each Ratings as Rating}
                            <Option value={Rating}>{Rating}</Option>
                        {/each}
                    </Select>
                </div>
            </div>
        {/each}
    </div>
    <div>
        <Button on:click={()=>{addNewRating()}} variant="outlined">
            <Label>Add a new rating</Label>
        </Button>
    </div>
    <div>
        <Button on:click={()=>{addRatings()}} variant="raised">
            <Label>Finish</Label>
        </Button>
    </div>
</div>

<style lang="css">
    .board {
        width: 100%;
		text-align: center;
		padding-top: 50px;
    }

    .addRating{
        display: flex;
        justify-content: center;

        padding-bottom: 12px;
    }

    .movie{
        width: 300px;
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