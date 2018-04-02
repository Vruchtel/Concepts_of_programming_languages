#include <iostream>
#include <setjmp.h>
#include <any>
#include <stack>
#include <string>
#include <cassert>

#define TRY {\
			jmp_buf env; \
			int isException = setjmp(env); \
			bool isEnvInStack = true; \
			currentObjectsStackSize = objectsStack.size();\
			if(!isException) { \
				environmentsStack.push(&env); \

#define THROW(e) if (isClearingStack) \
					std::terminate(); \
				currentException = e; \
				isClearingStack = true; \
				while(objectsStack.size() != currentObjectsStackSize) { \
					StackItem *currentObject = objectsStack.top(); \
					currentObject->~StackItem(); \
				} \
				isClearingStack = false; \
				if (!environmentsStack.empty()) \
					longjmp(*environmentsStack.top(), 1); \
				else \
					terminate();

#define CATCH(userExceptionType, userExceptionValue) } else \
	if (userExceptionType *p = std::any_cast<userExceptionType>(&currentException)) {\
		userExceptionType userExceptionValue = *p; \
		environmentsStack.pop(); \
		isEnvInStack = false;

#define FINALIZE } else { \
					if (isEnvInStack) {\
						environmentsStack.pop(); \
						isEnvInStack = false; \
					} \
					THROW(currentException); \
				} \
			}
	

std::any currentException;
std::stack<jmp_buf*> environmentsStack;

// структура, от которой должны наследоваться пользовательские классы, чтобы их можно было удалять при раскрутке стека
class StackItem {
public:
	StackItem();
	virtual ~StackItem();
};

// хранит ссылки на созданные объекты
std::stack<StackItem*> objectsStack;
int currentObjectsStackSize;
bool isClearingStack = false;

StackItem::StackItem() {
	objectsStack.push(this);
}

StackItem::~StackItem() {
	assert(!objectsStack.empty() && this == objectsStack.top());
	objectsStack.pop();
	std::cout << "Distruct object" << std::endl;
}


class A : public StackItem {
public:
	A() {
		std::cout << "create A" << std::endl;
	}
	~A() {
		std::cout << "distruct A" << std::endl;
	}
	void aa() {
		std::cout << "aa" << std::endl;
		THROW(5)
	}
	void ab() {
		std::cout << "ab" << std::endl;
		aa();
	}
};

class B : public StackItem {
public:
	B() {
		std::cout << "create B" << std::endl;
	}
	~B() {
		std::cout << "distruct B" << std::endl;
	}

	void ba() {
		std::cout << "ba" << std::endl;
		A a1;
		a1.ab();
	}

	void bb() {
		std::cout << "bb" << std::endl;
		ba();
	}
};

class C : public StackItem {
public:
	C() {
		std::cout << "create C" << std::endl;
	}
	C(const C& _c) {
		std::cout << "create C" << std::endl;
	}
	~C() {
		std::cout << "distruct C" << std::endl;
	}
	void ca() {
		std::cout << "ca" << std::endl;
		THROW('e');
	}
};

class D : public StackItem {
public:
	D() {
		std::cout << "create D" << std::endl;
	}
	~D() {
		std::cout << "distruct D" << std::endl;
		THROW(2.5)
	}
	void da(C paramC) {
		std::cout << "da" << std::endl;
		paramC.ca();
	}
};

int main() {

	// Simple example - учёт типизации
	TRY {
		std::cout << "There is no exception" << std::endl;
		TRY{
			std::cout << "New try, here throws exception" << std::endl;
			THROW(5.2f)
		}
		CATCH(char, e) {
			std::cout << "Here is char!" << std::endl;
		}
		FINALIZE
	}
	CATCH(int, e) {
		std::cout << "Here is int!" << std::endl;
	}
	CATCH(float, e) {
		std::cout << "Here is float!" << std::endl;
	}
	FINALIZE

	std::cout << std::endl;

	// Not so simple example - раскрутка стека
	TRY {
		B myB;
		myB.bb();
	}
	CATCH(int, e) {
		std::cout << "CATCH it!" << std::endl;
	}
	FINALIZE

	// One more example - удаление со стека параметров функции и аварийное завершение программы по повторному исключению
	// во время очистки стека
	TRY {
		D myD;
		C myC;
		myD.da(C(myC));
	}
	CATCH(char, e) {
		std::cout << "CATCH again!" << std::endl;
	}
	FINALIZE

	system("pause");
	return 0;
}