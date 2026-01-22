<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import {fetchGet} from "@/utilities/fetch.js";
import {ref, watch} from "vue";
import dayjs from "dayjs";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

const props = defineProps(['selectedPeer']);
const dashboardStore = DashboardConfigurationStore();

const startDate = ref(dayjs().subtract(6, 'day').format('YYYY-MM-DD'));
const endDate = ref(dayjs().format('YYYY-MM-DD'));
const report = ref(null);
const loading = ref(false);

const fetchReport = async () => {
	if (!props.selectedPeer) return;
	loading.value = true;
	await fetchGet('/api/getPeerUsageReport', {
		configurationName: props.selectedPeer.configuration.Name,
		id: props.selectedPeer.id,
		startDate: startDate.value,
		endDate: endDate.value
	}, (res) => {
		if (res.status){
			report.value = res.data;
		}else{
			report.value = null;
			dashboardStore.newMessage('WGDashboard', res.message || 'Failed to load usage report', 'danger');
		}
		loading.value = false;
	})
}

const setPreset = (days: number) => {
	startDate.value = dayjs().subtract(days - 1, 'day').format('YYYY-MM-DD');
	endDate.value = dayjs().format('YYYY-MM-DD');
};

const downloadCSV = () => {
	if (!props.selectedPeer) return;
	const url = `/api/getPeerUsageReportCSV?configurationName=${props.selectedPeer.configuration.Name}&id=${props.selectedPeer.id}&startDate=${startDate.value}&endDate=${endDate.value}`;
	window.open(url, '_blank');
};

watch(() => props.selectedPeer?.id, async () => {
	startDate.value = dayjs().subtract(6, 'day').format('YYYY-MM-DD');
	endDate.value = dayjs().format('YYYY-MM-DD');
	await fetchReport();
}, {immediate: true});

watch([startDate, endDate], async () => {
	await fetchReport();
});
</script>

<template>
	<div class="card rounded-3 bg-transparent">
		<div class="card-body">
			<div class="d-flex align-items-center gap-2 mb-2">
				<h6 class="text-muted mb-0">
					<LocaleText t="Usage Report"></LocaleText>
				</h6>
				<button class="btn btn-sm btn-outline-secondary ms-auto" @click="setPreset(7)">
					<LocaleText t="Last 7 Days"></LocaleText>
				</button>
				<button class="btn btn-sm btn-outline-secondary" @click="setPreset(30)">
					<LocaleText t="Last 30 Days"></LocaleText>
				</button>
				<button class="btn btn-sm btn-outline-primary" @click="downloadCSV" :disabled="loading">
					<LocaleText t="Download CSV"></LocaleText>
				</button>
			</div>
			<div class="d-flex flex-wrap gap-2 mb-3">
				<div>
					<label class="form-label text-muted mb-1"><small><LocaleText t="Start Date"></LocaleText></small></label>
					<input type="date" class="form-control form-control-sm" v-model="startDate">
				</div>
				<div>
					<label class="form-label text-muted mb-1"><small><LocaleText t="End Date"></LocaleText></small></label>
					<input type="date" class="form-control form-control-sm" v-model="endDate">
				</div>
				<div class="ms-auto" v-if="report">
					<label class="form-label text-muted mb-1"><small><LocaleText t="Range Total"></LocaleText></small></label>
					<div class="small">
						<strong>{{ (report.total.total_gb || 0).toFixed(4) }}</strong> GB
						<span class="text-muted ms-2">
							<LocaleText t="Sent"></LocaleText>: {{ (report.total.sent_gb || 0).toFixed(4) }} GB
							• <LocaleText t="Received"></LocaleText>: {{ (report.total.receive_gb || 0).toFixed(4) }} GB
						</span>
					</div>
				</div>
			</div>
			<div v-if="report" class="table-responsive">
				<table class="table table-sm table-striped align-middle">
					<thead>
						<tr>
							<th><LocaleText t="Date"></LocaleText></th>
							<th><LocaleText t="Total"></LocaleText> (GB)</th>
							<th><LocaleText t="Sent"></LocaleText> (GB)</th>
							<th><LocaleText t="Received"></LocaleText> (GB)</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="d in report.daily" :key="d.date">
							<td>{{ d.date }}</td>
							<td>{{ (d.total_gb || 0).toFixed(4) }}</td>
							<td>{{ (d.sent_gb || 0).toFixed(4) }}</td>
							<td>{{ (d.receive_gb || 0).toFixed(4) }}</td>
						</tr>
					</tbody>
				</table>
			</div>
			<div v-else class="text-muted">
				<small v-if="loading"><LocaleText t="Loading"></LocaleText>...</small>
				<small v-else><LocaleText t="No data"></LocaleText></small>
			</div>
		</div>
	</div>
</template>

<style scoped>
</style>
