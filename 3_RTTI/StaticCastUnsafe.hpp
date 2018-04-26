#pragma once
#include <type_traits>

template <typename TDest, typename TSource>
TDest staticCastUnsafeImpl(TSource* source, long dummyA, decltype(static_cast<TDest>(source))* dummy = nullptr) {
	return static_cast<TDest>(source);
}

template <typename TDest, typename TSource>
TDest staticCastUnsafeImpl(TSource*, char) {
	return nullptr;
}

template <typename TDest, typename TSource>
TDest staticCastUnsafe(TSource* source) {
	return staticCastUnsafeImpl<TDest>(source, 0L);
}
