#!/bin/bash
# Brain Find (bf) - Simple search wrapper for brain POC

BRAIN_POC_DIR="/Users/tarive/brain-poc"
QUERY="$*"

if [ -z "$QUERY" ]; then
    echo "Usage: bf <search query>"
    echo "Example: bf 'keep up good work'"
    exit 1
fi

# Run the Python search with improved scoring
cd "$BRAIN_POC_DIR"
python3 << EOF
import sys
sys.path.append('$BRAIN_POC_DIR/scripts')
sys.path.append('$BRAIN_POC_DIR')

try:
    from improved_scoring import ImprovedBrainScoring
except ImportError:
    # Fallback to regular scoring if improved not available
    from scripts.poc_scoring import BrainPOCScoring as ImprovedBrainScoring

brain = ImprovedBrainScoring()
query = "$QUERY"

print(f"🔍 Searching: '{query}'")
print("-" * 40)

# Try to detect project from query, otherwise search all
project_context = None
if "dci" in query.lower() or "ekren" in query.lower():
    project_context = "dci-analysis"
elif "econ" in query.lower() or "thrc" in query.lower():
    project_context = "econ-data"

results = brain.search_with_scoring(query, project_context=project_context)

if results:
    for i, result in enumerate(results[:3], 1):
        score = result['relevance_score']
        content = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
        
        print(f"\n{i}. Score: {score:.3f}")
        print(f"   {content}")
else:
    print("❌ No results found")
EOF