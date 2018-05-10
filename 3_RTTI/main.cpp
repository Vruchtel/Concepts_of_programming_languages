#include <iostream>
#include <map>
#include <set>
#include <string>
#include <cstring>
#include <vector>
#include <math.h>

#include "MacrosDefinitions.h"

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

	std::map<std::string, void*> tmap;
};

template <typename T>
class TMapWriter {
public:
	TMapWriter() {
		T *self = static_cast<T*>(this);
		self->tmap.insert({ T::GetStaticClassName(), self });
	}
};

// something that TYPEID returns
struct typeId {	
	typeId(std::string _className, std::string _parentClassesStr) : className(_className) {}

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
};

template <typename T>
typeId GetTypeId() {
	return typeId();
}

template <typename T>
typeId GetTypeId(T) {
	return GetTypeId<T>();
}

template <typename DestType>
DestType* DynamicCast(BaseParent *objectPtr) {
	// know real type of the object
	std::string realTypeName = objectPtr->GetClassName();
	
	std::string destTypeName = DestType::GetStaticClassName();

	auto it = objectPtr->tmap.find(destTypeName);
	if (it != objectPtr->tmap.end()) {
		return static_cast<DestType*>(it->second);
	}

	return nullptr;
}

/*TEST CLASSES*/

USE_RTTI(A) class A : BASE_PARENT(A) {
public:
	GET_CLASS_NAME(A)
	int a;
};

USE_RTTI(B, A) class B : public A, BASE_PARENT(B) {
public:
	GET_CLASS_NAME(B)
	int b;
};

USE_RTTI(C) class C : BASE_PARENT(C) {
public:
	GET_CLASS_NAME(C)
	int c;
};


USE_RTTI(D, B, C) class D : public B, public C, BASE_PARENT(D) {
public:
	GET_CLASS_NAME(D)
	int d;
};

int main() {
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
	std::cout << std::endl;

	A *aa = new A();
	A *ab = new B();
	A *ad = new D();
	B *bd = new D();
	C *cd = new D();
	D *dd = new D();

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
	B *bcd = DynamicCast<B>(cd);				// it works ok (sidecast)
	std::cout << "bcd " << bcd << std::endl;

	std::cout << std::endl;
	std::cout << "bd " << bd << std::endl;
	C *cbd = DynamicCast<C>(bd);				// it works ok (sidecast)
	std::cout << "cbd " << cbd << std::endl;

	std::cout << std::endl;
	std::cout << "aa " << aa << std::endl;
	C *caa = DynamicCast<C>(aa);				// it doesn't work
	std::cout << "caa " << caa << std::endl;

	std::cout << std::endl;
	std::cout << "ab " << ab << std::endl;
	C *cab = DynamicCast<C>(ab);				// it doesn't work
	std::cout << "cab " << cab << std::endl;

	system("pause");
	return 0;
}