<script>
    import Router from 'svelte-spa-router';

    import Main from './components/MainContents.svelte';
    import Adding from './components/AddContents.svelte';
    import Recommends from './components/RecContents.svelte';
    import Searching from './components/SearchContents.svelte';

    import { fade } from 'svelte/transition';

    const routes = {
        '/': Main,
        '/add': Adding,
        '/rec/:userid': Recommends,
		'/search': Searching
    };
</script>

<div class="appBoard" in:fade out:fade>
    <div class="title">
		<h1>Movie Recommendation</h1>
	</div>
    <Router {routes} />
</div>

<style>
    .appBoard {
        width: 100%;
        text-align: center;
		padding-top: 50px;
    }

    .title{
		margin-bottom: 50px;
	}
</style>