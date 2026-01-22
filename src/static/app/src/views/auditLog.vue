<script setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";

const rows = ref([]);
const loaded = ref(false);
let interval = null;

const getData = () => {
	fetchGet("/api/auditLog", {limit: 200}, (res) => {
		rows.value = res.data || [];
		loaded.value = true;
	});
};

onMounted(() => {
	getData();
	interval = setInterval(() => {
		getData();
	}, 15000);
});

onBeforeUnmount(() => {
	clearInterval(interval);
});
</script>

<template>
	<div class="text-body">
		<div class="d-flex align-items-center mb-3">
			<h3 class="mb-0">
				<i class="bi bi-clipboard-data me-2"></i>
				<LocaleText t="Audit Log"></LocaleText>
			</h3>
		</div>

		<div class="card rounded-3 shadow">
			<div class="card-body p-0">
				<table class="table table-sm mb-0" v-if="loaded">
					<thead>
					<tr>
						<th><LocaleText t="Date"></LocaleText></th>
						<th><LocaleText t="Actor"></LocaleText></th>
						<th><LocaleText t="IP"></LocaleText></th>
						<th><LocaleText t="Action"></LocaleText></th>
						<th><LocaleText t="Result"></LocaleText></th>
						<th><LocaleText t="Message"></LocaleText></th>
					</tr>
					</thead>
					<tbody>
					<tr v-for="row in rows" :key="row.LogID">
						<td class="text-muted">{{ row.LogDate }}</td>
						<td>{{ row.Actor }}</td>
						<td>{{ row.IP }}</td>
						<td class="text-muted">{{ row.Method }} {{ row.Path }}</td>
						<td>
							<span class="badge" :class="row.Result === 'true' ? 'text-bg-success' : 'text-bg-danger'">
								{{ row.Result === 'true' ? 'ok' : 'fail' }}
							</span>
						</td>
						<td class="text-muted">{{ row.Message }}</td>
					</tr>
					</tbody>
				</table>
				<div v-else class="p-3 text-muted">
					<span class="spinner-border spinner-border-sm me-2"></span>
					<LocaleText t="Loading"></LocaleText>
				</div>
			</div>
		</div>
	</div>
</template>
