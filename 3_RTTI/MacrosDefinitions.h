#pragma once

#define RET_SHARP(x) #x

// ... for all parents
#define USE_RTTI(className, ...) class className; \
							std::string className##_parentClassesStr = RET_SHARP((__VA_ARGS__));\
							template<> typeId GetTypeId<className>() { return typeId(#className, className##_parentClassesStr); }

#define TYPEID(object) GetTypeId(object)

#define BASE_PARENT(className) public virtual BaseParent, private TMapWriter<className>

#define GET_CLASS_NAME(className) virtual std::string GetClassName() { return #className; }\
								static std::string GetStaticClassName() {return #className; }