<script>
import { push } from 'svelte-spa-router';
import { fade } from 'svelte/transition';

let userid = '';

function goRec() {
    push(`/rec/${userid}`)
}

</script>

<div class="board" in:fade out:fade>
	<div class="userID">
		<input type="text" placeholder="enter userID" bind:value={userid} />
		<button on:click={goRec}>Predict</button>
	</div>
</div>

<style lang="css">
    .board {
        width: 100%;
		text-align: center;
		padding-top: 50px;
    }

	.userID{
		margin-bottom: 50px;
	}
</style>