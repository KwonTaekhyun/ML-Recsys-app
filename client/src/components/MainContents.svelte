<script>
import { push } from 'svelte-spa-router';
import Button, { Label } from '@smui/button';

const goSearch = () => {
        push('/search');
};
const goAdd = () => {
        push('/add');
};
</script>

<div class="board">
    <div class="links">
        <Button
            on:click={goSearch}
            variant="outlined"
        >
            <Label>기존 User에 대한 영화 Recomendation</Label>
        </Button>
    </div>
    <div class="links">
        <Button
            on:click={goAdd}
            variant="raised"
        >
            <Label>새로운 User에 대한 영화 Recomendation</Label>
        </Button>
    </div>
</div>

<style lang="css">
    .board {
        width: 100%;
		text-align: center;
		padding-top: 50px;
    }

    .links {
        padding-bottom: 20px;
    }
</style>