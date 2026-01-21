<script setup lang="ts" async>
import {useRoute, useRouter} from "vue-router";
import { fetchGet, fetchPost } from "@/utilities/fetch.js"


import {DashboardClientAssignmentStore} from "@/stores/DashboardClientAssignmentStore.js";
import { DashboardConfigurationStore } from "@/stores/DashboardConfigurationStore.js"

import {computed, reactive, ref, watch} from "vue";
import LocaleText from "@/components/text/localeText.vue";
import ClientAssignedPeers from "@/components/clientComponents/clientAssignedPeers.vue";
import ClientResetPassword from "@/components/clientComponents/clientResetPassword.vue";
import ClientDelete from "@/components/clientComponents/clientDelete.vue";
const assignmentStore = DashboardClientAssignmentStore()
const dashboardConfigurationStore = DashboardConfigurationStore()

const route = useRoute()
const router = useRouter()
const client = computed(() => {
	return assignmentStore.getClientById(route.params.id)
})
const clientAssignedPeers = ref({})
const usageSummary = ref(null)
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
const emits = defineEmits(['deleteSuccess'])

const clientProfile = reactive({
	Name: undefined
})
const formatGB = (v) => {
	const n = Number(v)
	if (Number.isNaN(n)) return "0.000"
	return n.toFixed(3)
}

if (client.value){
	watch(() => client.value.ClientID, async () => {
		clientProfile.Name = client.value.Name;
		await getAssignedPeers()
		await getUsageSummary()
	})
	await getAssignedPeers()
	await getUsageSummary()
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
			<div class="row g-3">
				<div class="col-lg-4">
					<div class="card rounded-3 h-100">
						<div class="card-body">
							<small class="text-muted">
								<LocaleText t="Total Usage"></LocaleText>
							</small>
							<div class="h4 mb-1">{{ formatGB(usageSummary.total.total_gb) }} GB</div>
							<div class="small text-muted">
								<LocaleText t="Sent"></LocaleText>: {{ formatGB(usageSummary.total.sent_gb) }} GB
								<span class="mx-2">•</span>
								<LocaleText t="Received"></LocaleText>: {{ formatGB(usageSummary.total.receive_gb) }} GB
							</div>
						</div>
					</div>
				</div>
				<div class="col-lg-4">
					<div class="card rounded-3 h-100">
						<div class="card-body">
							<small class="text-muted">
								<LocaleText t="Today"></LocaleText>
								<span class="ms-1">({{ usageSummary.daily.date }})</span>
							</small>
							<div class="h4 mb-1">{{ formatGB(usageSummary.daily.total_gb) }} GB</div>
							<div class="small text-muted">
								<LocaleText t="Sent"></LocaleText>: {{ formatGB(usageSummary.daily.sent_gb) }} GB
								<span class="mx-2">•</span>
								<LocaleText t="Received"></LocaleText>: {{ formatGB(usageSummary.daily.receive_gb) }} GB
							</div>
						</div>
					</div>
				</div>
				<div class="col-lg-4">
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
