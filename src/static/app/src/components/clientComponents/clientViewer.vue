<script setup lang="ts" async>
import {useRoute, useRouter} from "vue-router";
import { fetchGet, fetchPost } from "@/utilities/fetch.js"


import {DashboardClientAssignmentStore} from "@/stores/DashboardClientAssignmentStore.js";
import { DashboardConfigurationStore } from "@/stores/DashboardConfigurationStore.js"

import {computed, reactive, ref, watch, onBeforeUnmount} from "vue";
import LocaleText from "@/components/text/localeText.vue";
import ClientAssignedPeers from "@/components/clientComponents/clientAssignedPeers.vue";
import ClientResetPassword from "@/components/clientComponents/clientResetPassword.vue";
import ClientDelete from "@/components/clientComponents/clientDelete.vue";
import Sparkline from "@/components/visualComponents/sparkline.vue";
const assignmentStore = DashboardClientAssignmentStore()
const dashboardConfigurationStore = DashboardConfigurationStore()

const route = useRoute()
const router = useRouter()
const client = computed(() => {
	return assignmentStore.getClientById(route.params.id)
})
const clientAssignedPeers = ref({})
const usageSummary = ref(null)
const realtimeUsage = ref({sent_bps: 0, recv_bps: 0, updated_at: null})
const realtimeHistory = ref({sent: [], recv: []})
const rateUnit = ref(window.localStorage.getItem('wgdashboard_rate_unit') || 'Mbps')
const maxRateSamples = 30
const getAssignedPeers = async () => {
	await fetchGet('/api/clients/assignedPeers', {
		ClientID: client.value.ClientID
	}, (res) => {
		clientAssignedPeers.value = res.data;
	})
}
const getUsageSummary = async () => {
	await fetchGet('/api/clients/usageSummary', {
		ClientID: client.value.ClientID
	}, (res) => {
		usageSummary.value = res.data;
	})
}
const getRealtimeUsage = async () => {
	await fetchGet('/api/clients/realtimeUsage', {
		ClientID: client.value.ClientID
	}, (res) => {
		realtimeUsage.value = res.data || {sent_bps: 0, recv_bps: 0, updated_at: null}
		const sent = Number(realtimeUsage.value.sent_bps || 0)
		const recv = Number(realtimeUsage.value.recv_bps || 0)
		realtimeHistory.value.sent.push(sent)
		realtimeHistory.value.recv.push(recv)
		if (realtimeHistory.value.sent.length > maxRateSamples) realtimeHistory.value.sent.shift()
		if (realtimeHistory.value.recv.length > maxRateSamples) realtimeHistory.value.recv.shift()
	})
}
const emits = defineEmits(['deleteSuccess'])

const clientProfile = reactive({
	Name: undefined
})
const formatUsage = (gb) => {
	const n = Number(gb)
	if (!Number.isFinite(n)) return "0 MB"
	const abs = Math.abs(n)
	if (abs >= 1024) return `${(n / 1024).toFixed(2)} TB`
	if (abs >= 1) return `${n.toFixed(2)} GB`
	return `${(n * 1024).toFixed(2)} MB`
}
const formatRate = (bps) => {
	const v = Number(bps || 0)
	if (rateUnit.value === 'MB/s'){
		return `${(v / 1000000).toFixed(2)} MB/s`
	}
	return `${(v * 8 / 1000000).toFixed(2)} Mbps`
}
const updateRateUnit = (e) => {
	rateUnit.value = e.target.value
	window.localStorage.setItem('wgdashboard_rate_unit', rateUnit.value)
}

if (client.value){
	watch(() => client.value.ClientID, async () => {
		realtimeHistory.value = {sent: [], recv: []}
		clientProfile.Name = client.value.Name;
		await getAssignedPeers()
		await getUsageSummary()
		await getRealtimeUsage()
	})
	await getAssignedPeers()
	await getUsageSummary()
	await getRealtimeUsage()
	clientProfile.Name = client.value.Name
}else{
	router.push('/clients')
	dashboardConfigurationStore.newMessage("WGDashboard", "Client does not exist", "danger")
}



const updatingProfile = ref(false)
const updateProfile = async () => {
	updatingProfile.value = true
	await fetchPost("/api/clients/updateProfileName", {
		ClientID: client.value.ClientID,
		Name: clientProfile.Name
	}, (res) => {
		if (res.status){
			client.value.Name = clientProfile.Name;
			dashboardConfigurationStore.newMessage("Server", "Client name update success", "success")
		}else{
			clientProfile.Name = client.value.Name;
			dashboardConfigurationStore.newMessage("Server", "Client name update failed", "danger")
		}
		updatingProfile.value = false
	})
}
const deleteSuccess = async () => {
	await router.push('/clients')
	await assignmentStore.getClients()
}

const realtimeInterval = ref(undefined)
const setRealtimeInterval = () => {
	clearInterval(realtimeInterval.value)
	realtimeInterval.value = setInterval(async () => {
		await getRealtimeUsage()
	}, 5000)
}
setRealtimeInterval()
onBeforeUnmount(() => {
	clearInterval(realtimeInterval.value)
	realtimeInterval.value = undefined
})

</script>

<template>
	<div class="text-body d-flex flex-column overflow-y-scroll h-100" v-if="client" :key="client.ClientID">
		<div class="p-4 border-bottom bg-body-tertiary z-0">
			<div class="mb-3 backLink">
				<RouterLink to="/clients" class="text-body text-decoration-none">
					<i class="bi bi-arrow-left me-2"></i>
					Back</RouterLink>
			</div>
			<small class="text-muted">
				<LocaleText t="Email"></LocaleText>
			</small>
			<h1>
				{{ client.Email }}
			</h1>
			<div class="d-flex flex-column gap-2">
				<div class="d-flex align-items-center">
					<small class="text-muted">
						<LocaleText t="Client ID"></LocaleText>
					</small>
					<small class="ms-auto">
						<samp>{{ client.ClientID }}</samp>
					</small>
				</div>
				<div class="d-flex align-items-center gap-2">
					<small class="text-muted">
						<LocaleText t="Client Name"></LocaleText>
					</small>
					<input class="form-control form-control-sm rounded-3 ms-auto"
						   style="width: 300px"
						   type="text" v-model="clientProfile.Name">
					<button
						@click="updateProfile()"
						aria-label="Save Client Name"
						class="btn btn-sm rounded-3 bg-success-subtle border-success-subtle text-success-emphasis">
						<i class="bi bi-save-fill"></i>
					</button>
				</div>
			</div>
		</div>
		<div class="p-3 border-bottom" v-if="usageSummary">
			<div class="d-flex justify-content-end align-items-center gap-2 mb-2">
				<small class="text-muted"><LocaleText t="Realtime Units"></LocaleText></small>
				<select class="form-select form-select-sm w-auto" @change="updateRateUnit">
					<option value="Mbps" :selected="rateUnit === 'Mbps'">Mbps</option>
					<option value="MB/s" :selected="rateUnit === 'MB/s'">MB/s</option>
				</select>
			</div>
			<div class="row g-3">
				<div class="col-lg-3">
					<div class="card rounded-3 h-100">
						<div class="card-body">
							<small class="text-muted">
								<LocaleText t="Total Usage"></LocaleText>
							</small>
							<div class="h4 mb-1">{{ formatUsage(usageSummary.total.total_gb) }}</div>
							<div class="small text-muted">
								<LocaleText t="Sent"></LocaleText>: {{ formatUsage(usageSummary.total.sent_gb) }}
								<span class="mx-2">•</span>
								<LocaleText t="Received"></LocaleText>: {{ formatUsage(usageSummary.total.receive_gb) }}
							</div>
						</div>
					</div>
				</div>
				<div class="col-lg-3">
					<div class="card rounded-3 h-100">
						<div class="card-body">
							<small class="text-muted">
								<LocaleText t="Today"></LocaleText>
								<span class="ms-1">({{ usageSummary.daily.date }})</span>
							</small>
							<div class="h4 mb-1">{{ formatUsage(usageSummary.daily.total_gb) }}</div>
							<div class="small text-muted">
								<LocaleText t="Sent"></LocaleText>: {{ formatUsage(usageSummary.daily.sent_gb) }}
								<span class="mx-2">•</span>
								<LocaleText t="Received"></LocaleText>: {{ formatUsage(usageSummary.daily.receive_gb) }}
							</div>
						</div>
					</div>
				</div>
				<div class="col-lg-3">
					<div class="card rounded-3 h-100">
						<div class="card-body">
							<small class="text-muted">
								<LocaleText t="Assigned Peers"></LocaleText>
							</small>
							<div class="h4 mb-1">{{ usageSummary.peers_count }}</div>
							<div class="small text-muted">
								<LocaleText t="Updated"></LocaleText>: {{ usageSummary.generated_at }}
							</div>
						</div>
					</div>
				</div>
				<div class="col-lg-3">
					<div class="card rounded-3 h-100">
						<div class="card-body">
							<small class="text-muted">
								<LocaleText t="Realtime Speed"></LocaleText>
							</small>
							<div class="h5 mb-1">
								{{ formatRate(realtimeUsage.recv_bps) }} ↓
							</div>
							<div class="h6 text-muted mb-0">
								{{ formatRate(realtimeUsage.sent_bps) }} ↑
							</div>
							<div class="mt-2">
								<Sparkline
									:recv="realtimeHistory.recv"
									:sent="realtimeHistory.sent"
									:width="160"
									:height="34"
								/>
							</div>
							<div class="small text-muted mt-1">
								<LocaleText t="Updated"></LocaleText>: {{ realtimeUsage.updated_at || '—' }}
							</div>
						</div>
					</div>
				</div>
			</div>
			<div class="alert alert-warning mt-3 mb-0 py-2" v-if="usageSummary.tracking_disabled_configurations && usageSummary.tracking_disabled_configurations.length">
				<small>
					<LocaleText t="Traffic tracking disabled for"></LocaleText>:
					{{ usageSummary.tracking_disabled_configurations.join(', ') }}
				</small>
			</div>
		</div>
		<div style="flex: 1 0 0; overflow-y: scroll;">
			<ClientAssignedPeers
				@refresh="getAssignedPeers()"
				:clientAssignedPeers="clientAssignedPeers"
				:client="client"></ClientAssignedPeers>
<!--			<ClientResetPassword-->
<!--				:client="client" v-if="client.ClientGroup === 'Local'"></ClientResetPassword>-->
			<ClientDelete
				@deleteSuccess="deleteSuccess()"
				:client="client"></ClientDelete>
		</div>
	</div>
	<div v-else class="d-flex w-100 h-100 text-muted">
		<div class="m-auto text-center">
			<h1>
				<i class="bi bi-person-x"></i>
			</h1>
			<p>
				<LocaleText t="Client does not exist"></LocaleText>
			</p>
		</div>
	</div>
</template>

<style scoped>
@media screen and (min-width: 576px) {
	.backLink{
		display: none;
	}
}
</style>
