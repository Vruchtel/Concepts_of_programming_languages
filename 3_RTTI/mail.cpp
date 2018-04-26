#include <iostream>
#include <map>
#include <set>
#include <string>
#include <cstring>
#include <vector>
#include <math.h>

#include "StaticCastUnsafe.hpp"
#include "MacrosDefinitions.h"
#include "ConvertStringToSet.h"

/*template <typename T>
std::string GetClassName() {
	return GetTypeId<T>().className;
}*/

long hash(std::string str) {
	long result = 0;
	long p = 54059;
	for (int i = 0; i < str.size(); i++) {
		result += (static_cast<long>(pow(p, i)) * str[i]);
	}
	return result;
}

// base parent for each class wich uses rtti
class BaseParent {
public:
	virtual std::string GetClassName() { return "undefined"; }
	static std::string GetStaticClassName() { return "BaseParent"; }
};

// save information about all parents and all children
class ClassesGraph {
public:
	void AppendClassWithParents(std::string child, std::string parentsStr) {
		std::set<std::string> parentsSet = std::set<std::string>();
		ConvertStringToSet(parentsStr, parentsSet);

		classToParents[child] = parentsSet;
		for (std::string parent : parentsSet) {
			classToChildren[parent].insert(child);
		}
	}

	void CalculateExistanseOfPaths() {
		classToDeepParents = findPaths(classToParents);
		//classToDeepChildren = findPaths(classToChildren);
	}

	// check if there is any deep path from child to parent
	bool isDeepPathFromChildToParent(std::string child, std::string parent) {
		if (classToDeepParents[child].find(parent) != classToDeepParents[child].end()) {
			return true;
		}
		return false;
	}

	// check if there is any deep path from parent to child
	/*bool isDeepPathFromParentToChild(std::string parent, std::string child) {
		if (classToDeepChildren[parent].find(child) != classToDeepChildren[parent].end()) {
			return true;
		}
		return false;
	}*/

private:
	std::map<std::string, std::set<std::string>> classToParents;
	std::map<std::string, std::set<std::string>> classToChildren;

	std::map<std::string, std::set<std::string>> classToDeepParents;
	//std::map<std::string, std::set<std::string>> classToDeepChildren;

	// finds, if there is a path from one vertice to another
	// if one class is anothers child or one class is anothers parents
	// for all classes in graph
	// returns map <form -> to>
	std::map<std::string, std::set<std::string>> findPaths(const std::map<std::string, std::set<std::string>> &graph) {
		// dictionary <class name> -> <numerical id>
		std::map<std::string, int> nameToId = std::map<std::string, int>();
		// and inverted
		std::map<int, std::string> idToName = std::map<int, std::string>();
		int currentNum = 0;
		for (auto infoAboutOne : classToParents) {
			nameToId[infoAboutOne.first] = currentNum;
			idToName[currentNum] = infoAboutOne.first;
			++currentNum;
		}

		// create matrix for Floyd-Warshall
		std::vector<std::vector<bool>> matrix = std::vector< std::vector<bool>>(nameToId.size(), std::vector<bool>(nameToId.size(), false));
		for (auto infoAboutOne : graph) {
			std::string from = infoAboutOne.first;
			for (auto to : infoAboutOne.second) {
				matrix[nameToId[from]][nameToId[to]] = true;
			}
		}

		// Floyd-Warshall
		for (std::size_t iter = 0; iter < matrix.size(); iter++) {
			for (std::size_t row = 0; row < matrix.size(); row++) {
				for (std::size_t col = 0; col < matrix.size(); col++) {
					if (matrix[row][iter] && matrix[iter][col]) {
						matrix[row][col] = true;
					} // else - like it was before
				}
			}
		}
		// i'm my parent
		for (std::size_t i = 0; i < matrix.size(); i++) {
			matrix[i][i] = true;
		}

		// make result
		std::map<std::string, std::set<std::string>> result = std::map<std::string, std::set<std::string>>();
		for (std::size_t row = 0; row < matrix.size(); row++) {
			for (std::size_t col = 0; col < matrix.size(); col++) {
				if (matrix[row][col]) {
					result[idToName[row]].insert(idToName[col]);
				}
			}
		}

		return result;
	}
};

// GLOBAL GRAPH WITH INFORMATION ABOUT ALL CLASSES
ClassesGraph cg = ClassesGraph();

class AppenderToClassesGraph {
public:
	AppenderToClassesGraph(std::string child, std::string parentsStr) {
		cg.AppendClassWithParents(child, parentsStr);
	}
};

// something that TYPEID returns
struct typeId {	
	typeId(std::string _className, std::string _parentClassesStr) : className(_className) {
		// find all parents from string
		ConvertStringToSet(_parentClassesStr, parentClasses);
	}

	std::string name() { return className; }

	bool operator==(const typeId &another) const {
		return another.className == className;
	}

	bool operator!=(const typeId &another) const {
		return another.className != className;
	}

	long hash_code() const {
		return hash(className);
	}

private:
	std::string className;
	// direct parents
	std::set<std::string> parentClasses;
};

template <typename T>
typeId GetTypeId() {
	return typeId();
}

template <typename T>
typeId GetTypeId(T) {
	return GetTypeId<T>();
}

template <typename DestType, typename SourceType>
DestType* DynamicCast(SourceType *objectPtr) {
	// know real type of the object
	std::string realTypeName = objectPtr->GetClassName();
	
	std::string destTypeName = DestType::GetStaticClassName();
	std::string sourceTypeName = SourceType::GetStaticClassName();
	
	if (cg.isDeepPathFromChildToParent(realTypeName, sourceTypeName) 
		&& (cg.isDeepPathFromChildToParent(sourceTypeName, destTypeName) 
			|| cg.isDeepPathFromChildToParent(destTypeName, sourceTypeName))) {
		return staticCastUnsafe<DestType*>(objectPtr);
	}

	return nullptr;
}

/*TEST CLASSES*/

USE_RTTI(A) class A : BASE_PARENT {
public:
	GET_CLASS_NAME(A)
	int a;
};

USE_RTTI(B, A) class B : public A, BASE_PARENT {
public:
	GET_CLASS_NAME(B)
	int b;
};

USE_RTTI(C) class C : BASE_PARENT {
public:
	GET_CLASS_NAME(C)
	int c;
};


USE_RTTI(D, B, C) class D : public B, public C, BASE_PARENT {
public:
	GET_CLASS_NAME(D)
	int d;
};

int main() {
	cg.CalculateExistanseOfPaths();

	A a = A();
	B b = B();
	C c = C();
	D d = D();

	std::cout << "a type: " << TYPEID(a).name() << std::endl;
	std::cout << "b type: " << TYPEID(b).name() << std::endl;
	std::cout << "c type: " << TYPEID(c).name() << std::endl;
	std::cout << "d type: " << TYPEID(d).name() << std::endl;

	// test ==
	std::cout << std::endl;
	std::cout << "test ==" << std::endl;
	A a1 = A();
	std::cout << (TYPEID(a) == TYPEID(a1)) << std::endl;  // true
	std::cout << (TYPEID(a) == TYPEID(b)) << std::endl;  // false
	
	// test !=
	std::cout << std::endl;
	std::cout << "test !=" << std::endl;
	std::cout << (TYPEID(a) != TYPEID(a1)) << std::endl;  // false
	std::cout << (TYPEID(c) != TYPEID(d)) << std::endl;  // true

	// test hash_code
	std::cout << std::endl;
	std::cout << "hash_code" << std::endl;
	std::cout << TYPEID(a).hash_code() << std::endl;
	std::cout << TYPEID(c).hash_code() << std::endl;

	A *aa = new A();
	std::cout << aa->GetClassName() << std::endl; // A

	A *ab = new B();
	std::cout << ab->GetClassName() << std::endl; // B

	A *ad = new D();
	std::cout << ad->GetClassName() << std::endl; // D

	B *bd = new D();
	std::cout << bd->GetClassName() << std::endl; // D

	C *cd = new D();
	std::cout << cd->GetClassName() << std::endl; // D

	D *dd = new D();
	std::cout << dd->GetClassName() << std::endl; // D

	std::cout << std::endl;
	std::cout << "bd " << bd << std::endl;
	A *abd = DynamicCast<A>(bd);				// it works ok (A -> B -> D)
	std::cout << "abd " << abd << std::endl;

	std::cout << std::endl;
	std::cout << "dd " << dd << std::endl;
	C *cdd = DynamicCast<C>(dd);            // it works ok (B, C -> D)
	std::cout << "cdd " << cdd << std::endl;

	std::cout << std::endl;
	std::cout << "ad " << ad << std::endl;
	B *bad = DynamicCast<B>(ad);				// it works ok (A -> B -> D)
	std::cout << "bad " << bad << std::endl;

	std::cout << std::endl;
	std::cout << "ab " << ab << std::endl;
	B *bab = DynamicCast<B>(ab);				// it works ok (A -> B)
	std::cout << "bab " << bab << std::endl;

	std::cout << std::endl;
	std::cout << "dd " << dd << std::endl;
	D *ddd = DynamicCast<D>(dd);				// it works ok (D)
	std::cout << "ddd " << ddd << std::endl;

	std::cout << std::endl;
	std::cout << "cd " << cd << std::endl;
	B *bcd = DynamicCast<B>(cd);				// nullptr - impossible to convert
	std::cout << "bcd " << bcd << std::endl;

	std::cout << std::endl;
	std::cout << "bd " << bd << std::endl;
	C *cbd = DynamicCast<C>(bd);				// nullptr - impossible to convert
	std::cout << "cbd " << cbd << std::endl;


	system("pause");
	return 0;
}