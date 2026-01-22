<script setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";

const data = ref(null);
const loaded = ref(false);
let interval = null;

const getData = () => {
	fetchGet("/api/healthStatus", {}, (res) => {
		data.value = res.data;
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

const formatBytes = (bytes) => {
	if (bytes === null || bytes === undefined) return "-";
	const units = ["B", "KB", "MB", "GB", "TB"];
	let value = bytes;
	let unitIndex = 0;
	while (value >= 1024 && unitIndex < units.length - 1) {
		value /= 1024;
		unitIndex += 1;
	}
	return `${value.toFixed(2)} ${units[unitIndex]}`;
};

const formatCount = (value) => {
	if (value === null || value === undefined) return "-";
	return value.toLocaleString();
};

const serviceBadgeClass = (svc) => {
	return svc?.active ? "text-bg-success" : "text-bg-danger";
};
</script>

<template>
	<div class="text-body row g-3">
		<div class="col-12">
			<h3 class="mb-3">
				<i class="bi bi-heart-pulse-fill me-2"></i>
				<LocaleText t="Health"></LocaleText>
			</h3>
		</div>

		<div class="col-lg-6">
			<div class="card rounded-3 shadow h-100">
				<div class="card-header bg-transparent">
					<LocaleText t="Services"></LocaleText>
				</div>
				<div class="card-body">
					<table class="table table-sm align-middle mb-0" v-if="loaded">
						<thead>
						<tr>
							<th><LocaleText t="Service"></LocaleText></th>
							<th><LocaleText t="Status"></LocaleText></th>
							<th><LocaleText t="Enabled"></LocaleText></th>
						</tr>
						</thead>
						<tbody>
						<tr>
							<td>WGDashboard</td>
							<td>
								<span class="badge" :class="serviceBadgeClass(data?.services?.wg_dashboard)">
									{{ data?.services?.wg_dashboard?.status || "-" }}
								</span>
							</td>
							<td>{{ data?.services?.wg_dashboard?.enabled_state || "-" }}</td>
						</tr>
						<tr>
							<td>WireGuard (wg0)</td>
							<td>
								<span class="badge" :class="serviceBadgeClass(data?.services?.wireguard)">
									{{ data?.services?.wireguard?.status || "-" }}
								</span>
							</td>
							<td>{{ data?.services?.wireguard?.enabled_state || "-" }}</td>
						</tr>
						<tr>
							<td>AdGuard Home</td>
							<td>
								<span class="badge" :class="serviceBadgeClass(data?.services?.adguard)">
									{{ data?.services?.adguard?.status || "-" }}
								</span>
							</td>
							<td>{{ data?.services?.adguard?.enabled_state || "-" }}</td>
						</tr>
						</tbody>
					</table>
					<div v-else class="text-muted">
						<span class="spinner-border spinner-border-sm me-2"></span>
						<LocaleText t="Loading"></LocaleText>
					</div>
				</div>
			</div>
		</div>

		<div class="col-lg-6">
			<div class="card rounded-3 shadow h-100">
				<div class="card-header bg-transparent">
					<LocaleText t="WireGuard"></LocaleText>
				</div>
				<div class="card-body" v-if="loaded">
					<div class="d-flex justify-content-between mb-2">
						<span><LocaleText t="Total"></LocaleText></span>
						<span class="text-muted">{{ formatCount(data?.wireguard?.total_peers) }}</span>
					</div>
					<div class="d-flex justify-content-between mb-3">
						<span><LocaleText t="Connected"></LocaleText></span>
						<span class="text-muted">{{ formatCount(data?.wireguard?.connected_peers) }}</span>
					</div>
					<table class="table table-sm mb-0">
						<thead>
						<tr>
							<th><LocaleText t="Configuration"></LocaleText></th>
							<th><LocaleText t="Total"></LocaleText></th>
							<th><LocaleText t="Connected"></LocaleText></th>
						</tr>
						</thead>
						<tbody>
						<tr v-for="cfg in data?.wireguard?.configs" :key="cfg.name">
							<td class="text-muted">{{ cfg.name }}</td>
							<td>{{ formatCount(cfg.total_peers) }}</td>
							<td>{{ formatCount(cfg.connected_peers) }}</td>
						</tr>
						</tbody>
					</table>
				</div>
				<div v-else class="card-body text-muted">
					<span class="spinner-border spinner-border-sm me-2"></span>
					<LocaleText t="Loading"></LocaleText>
				</div>
			</div>
		</div>

		<div class="col-lg-6">
			<div class="card rounded-3 shadow h-100">
				<div class="card-header bg-transparent">
					<LocaleText t="AdGuard Home"></LocaleText>
				</div>
				<div class="card-body">
					<ul class="list-group list-group-flush" v-if="loaded">
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="DNS Bind"></LocaleText></span>
							<span class="text-muted">{{ data?.adguard?.dns_bind_hosts?.join(", ") || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="DNS Port"></LocaleText></span>
							<span class="text-muted">{{ data?.adguard?.dns_port || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="HTTP Address"></LocaleText></span>
							<span class="text-muted">{{ data?.adguard?.http_address || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="TLS Server Name"></LocaleText></span>
							<span class="text-muted">{{ data?.adguard?.tls_server_name || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="HTTPS Port"></LocaleText></span>
							<span class="text-muted">{{ data?.adguard?.tls_port_https || "-" }}</span>
						</li>
					</ul>
					<div v-else class="text-muted">
						<span class="spinner-border spinner-border-sm me-2"></span>
						<LocaleText t="Loading"></LocaleText>
					</div>
				</div>
			</div>
		</div>

		<div class="col-lg-6">
			<div class="card rounded-3 shadow h-100">
				<div class="card-header bg-transparent">
					<LocaleText t="AdGuard Query Stats"></LocaleText>
				</div>
				<div class="card-body" v-if="loaded">
					<ul class="list-group list-group-flush">
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Window (minutes)"></LocaleText></span>
							<span class="text-muted">{{ data?.adguard_query_stats?.window_minutes }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Total Queries"></LocaleText></span>
							<span class="text-muted">{{ formatCount(data?.adguard_query_stats?.total) }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Blocked"></LocaleText></span>
							<span class="text-muted">{{ formatCount(data?.adguard_query_stats?.blocked) }} ({{ data?.adguard_query_stats?.blocked_percent }}%)</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Last Entry"></LocaleText></span>
							<span class="text-muted">{{ data?.adguard_query_stats?.last_entry || "-" }}</span>
						</li>
					</ul>
					<div
						v-if="data?.adguard_query_stats && (data.adguard_query_stats.status === 'ok' || data.adguard_query_stats.status === 'empty') && (data.adguard_query_stats.total || 0) === 0"
						class="text-muted mt-2"
					>
						<LocaleText t="No queries in last window"></LocaleText>
					</div>
				</div>
				<div v-else class="card-body text-muted">
					<span class="spinner-border spinner-border-sm me-2"></span>
					<LocaleText t="Loading"></LocaleText>
				</div>
			</div>
		</div>

		<div class="col-lg-6">
			<div class="card rounded-3 shadow h-100">
				<div class="card-header bg-transparent">
					<LocaleText t="Certificate"></LocaleText>
				</div>
				<div class="card-body">
					<ul class="list-group list-group-flush" v-if="loaded">
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Path"></LocaleText></span>
							<span class="text-muted">{{ data?.certificate?.path || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Expires"></LocaleText></span>
							<span class="text-muted">{{ data?.certificate?.not_after || data?.certificate?.status || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Days Remaining"></LocaleText></span>
							<span class="text-muted">{{ data?.certificate?.days_remaining ?? "-" }}</span>
						</li>
					</ul>
					<div v-else class="text-muted">
						<span class="spinner-border spinner-border-sm me-2"></span>
						<LocaleText t="Loading"></LocaleText>
					</div>
				</div>
			</div>
		</div>

		<div class="col-lg-6">
			<div class="card rounded-3 shadow h-100">
				<div class="card-header bg-transparent">
					<LocaleText t="Certificate Renewal"></LocaleText>
				</div>
				<div class="card-body" v-if="loaded">
					<ul class="list-group list-group-flush">
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Method"></LocaleText></span>
							<span class="text-muted">{{ data?.certificate_renewal?.method || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Timer"></LocaleText></span>
							<span class="text-muted">{{ data?.certificate_renewal?.timer_unit || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Next Run"></LocaleText></span>
							<span class="text-muted">{{ data?.certificate_renewal?.next_run || "-" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Last Run"></LocaleText></span>
							<span class="text-muted">{{ data?.certificate_renewal?.last_run || "-" }}</span>
						</li>
					</ul>
				</div>
				<div v-else class="card-body text-muted">
					<span class="spinner-border spinner-border-sm me-2"></span>
					<LocaleText t="Loading"></LocaleText>
				</div>
			</div>
		</div>

		<div class="col-lg-6">
			<div class="card rounded-3 shadow h-100">
				<div class="card-header bg-transparent">
					<LocaleText t="Disk"></LocaleText>
				</div>
				<div class="card-body">
					<ul class="list-group list-group-flush" v-if="loaded">
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Mount"></LocaleText></span>
							<span class="text-muted">{{ data?.disk?.mount || "/" }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Used"></LocaleText></span>
							<span class="text-muted">{{ formatBytes(data?.disk?.used) }} ({{ data?.disk?.percent }}%)</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Free"></LocaleText></span>
							<span class="text-muted">{{ formatBytes(data?.disk?.free) }}</span>
						</li>
						<li class="list-group-item d-flex justify-content-between">
							<span><LocaleText t="Total"></LocaleText></span>
							<span class="text-muted">{{ formatBytes(data?.disk?.total) }}</span>
						</li>
					</ul>
					<div v-else class="text-muted">
						<span class="spinner-border spinner-border-sm me-2"></span>
						<LocaleText t="Loading"></LocaleText>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
