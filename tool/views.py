from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from tool.utils.calc_cont import cont_calculations
from .models import Test
from .serializers import TestSerializer

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"])
    def calc_continuous_metric(self, request):
        # Extracting payload from request
        payload = request.data
        
        try:
            confidence_level = float(payload.get('confidence_level', 95.0))
            power = float(payload.get('power', 80.0))
            baseline_kpi = float(payload.get('baseline_kpi', 5.0))
            standard_deviation = float(payload.get('standard_deviation', 1.5))
            mde = float(payload.get('mde', 0.5))
            absolute = payload.get('absolute', True) in [True, 'true', 'True', 1, '1']
            arms = int(payload.get('arms', 2))
            daily_interactions = int(payload.get('daily_interactions', 1000))
            two_tailed = payload.get('two_tailed', True) in [True, 'true', 'True', 1, '1']
            equal_allocation = payload.get('equal_allocation', True) in [True, 'true', 'True', 1, '1']
            revenue_per_conversion = float(payload.get('revenue_per_conversion', 100.0))
            expected_uplift = float(payload.get('expected_uplift', 0.10))
            allocations = payload.get('allocations', {})

        except ValueError as e:
            return Response({"error": "Invalid input types", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call cont_calculations function
        try:
            results = cont_calculations(
                confidence_level, power, baseline_kpi, standard_deviation, mde,
                absolute, arms, daily_interactions, two_tailed, equal_allocation,
                revenue_per_conversion, expected_uplift, allocations
            )
        except Exception as e:
            return Response({"error": "Calculation error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Return results
        return Response(results, status=status.HTTP_200_OK)
