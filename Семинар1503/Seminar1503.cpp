// Seminar1503.cpp: определяет точку входа для консольного приложения.
//

#include "stdafx.h"

#include <string>
#include <iostream>
#include <unordered_map>
#include <unordered_set>

// https://colab.research.google.com/drive/1kTsyM-NUCD50OPUWwLfxIY8skd6VOJwi#scrollTo=to7dIccqD35t
// https://ideone.com/an91pX

class Graph {
public:
	std::unordered_map<char, std::unordered_set<char>> vertices;
};

class VisualizationCallback {
public:
	void discoverVertex(char v) {
		std::cout << "->" << v << " ";
	}
	void finishVertex(char v) {
		std::cout << v << "-> ";
	}
};

template<typename Callback>
void dfs(Graph graph, char start, Callback callback, std::unordered_set<char> &visited) {
	visited.insert(start);
	//std::cout << start << " ";
	callback.discoverVertex(start);
	for (auto v : graph.vertices[start]) {
		if (visited.find(v) == visited.end()) {
			dfs(graph, v, callback, visited);
		}
	}
	callback.finishVertex(start);
}


int main()
{
	std::unordered_map<char, std::unordered_set<char>> vert{
		{ 'A',{ { 'B', 'C' } } },
		{ 'B',{ { 'A', 'D', 'E' } } },
		{ 'C',{ { 'A', 'F' } } },
		{ 'D',{ { 'B' } } },
		{ 'E',{ { 'B', 'F' } } },
		{ 'F',{ { 'C', 'E' } } }
	};

	Graph g;
	g.vertices = vert;

	VisualizationCallback vc;
	dfs(g, 'A', vc, std::unordered_set<char>());

    return 0;
}

