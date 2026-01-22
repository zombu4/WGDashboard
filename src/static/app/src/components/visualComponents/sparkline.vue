<script setup>
import { computed } from "vue";

const props = defineProps({
	recv: { type: Array, default: () => [] },
	sent: { type: Array, default: () => [] },
	width: { type: Number, default: 120 },
	height: { type: Number, default: 24 },
	strokeRecv: { type: String, default: "#0d6efd" },
	strokeSent: { type: String, default: "#198754" }
});

const seriesStats = computed(() => {
	const all = [...props.recv, ...props.sent].map(n => Number(n)).filter(n => Number.isFinite(n));
	if (all.length === 0) return { min: 0, max: 1 };
	const min = Math.min(...all);
	const max = Math.max(...all);
	return { min, max: max === min ? min + 1 : max };
});

const buildPoints = (arr) => {
	if (!arr || arr.length === 0) return "";
	const { min, max } = seriesStats.value;
	const range = max - min || 1;
	const count = arr.length;
	const width = props.width;
	const height = props.height;
	return arr.map((v, i) => {
		const x = count === 1 ? 0 : (i / (count - 1)) * width;
		const y = height - ((Number(v) - min) / range) * height;
		return `${x},${y}`;
	}).join(" ");
};

const recvPoints = computed(() => buildPoints(props.recv));
const sentPoints = computed(() => buildPoints(props.sent));
const hasData = computed(() => (props.recv && props.recv.length) || (props.sent && props.sent.length));
</script>

<template>
	<svg
		:width="width"
		:height="height"
		:viewBox="`0 0 ${width} ${height}`"
		preserveAspectRatio="none"
		class="sparkline"
	>
		<polyline
			v-if="hasData"
			:points="recvPoints"
			:stroke="strokeRecv"
			fill="none"
			stroke-width="1.4"
			stroke-linecap="round"
			stroke-linejoin="round"
		/>
		<polyline
			v-if="hasData"
			:points="sentPoints"
			:stroke="strokeSent"
			fill="none"
			stroke-width="1.4"
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-dasharray="2,2"
		/>
	</svg>
</template>

<style scoped>
.sparkline {
	display: block;
}
</style>
